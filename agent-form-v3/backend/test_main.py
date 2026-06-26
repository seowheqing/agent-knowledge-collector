"""单元测试 - 知识库材料解析功能"""
import os
import pytest
from main import parse_txt, parse_file, parse_docx, parse_excel


# 测试1：能从文本里提取QA对
def test_parse_qa():
    with open("tmp_qa.txt", "w", encoding="utf-8") as f:
        f.write("问：保修多久？\n答：所有产品保修三年。\n\n问：怎么退货？\n答：联系客服即可。")
    
    result = parse_txt("tmp_qa.txt")
    
    assert len(result) == 2
    assert result[0]["type"] == "qa"
    assert "保修" in result[0]["title"]
    assert "三年" in result[0]["content"]
    assert result[1]["type"] == "qa"
    assert "退货" in result[1]["title"]
    
    os.remove("tmp_qa.txt")


# 测试2：普通文本按段落分割
def test_parse_plain_text():
    with open("tmp_plain.txt", "w", encoding="utf-8") as f:
        f.write("这是第一段内容，介绍我们的产品。\n\n这是第二段内容，介绍服务流程。")
    
    result = parse_txt("tmp_plain.txt")
    
    assert len(result) == 2
    assert result[0]["type"] == "document"
    assert "第一段" in result[0]["content"]
    
    os.remove("tmp_plain.txt")


# 测试3：不认识的文件格式不会崩
def test_unknown_format():
    result = parse_file("fake.xyz", "fake.xyz")
    assert len(result) == 1
    assert result[0]["type"] == "unknown"


# 测试4：空文件不会报错
def test_empty_file():
    with open("tmp_empty.txt", "w") as f:
        f.write("")
    
    result = parse_txt("tmp_empty.txt")
    assert result == []
    
    os.remove("tmp_empty.txt")


# 测试5：压缩包识别正确
def test_archive_detection():
    result = parse_file("docs.zip", "docs.zip")
    assert result[0]["type"] == "archive"
    assert "压缩包" in result[0]["title"]
