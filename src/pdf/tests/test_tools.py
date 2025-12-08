import pytest

from pdf import mcp


def get_tool(name: str):
    """Get a tool function by name."""
    return mcp._tool_manager._tools[name].fn


class TestExtractText:
    def test_extract_all_pages(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf))

        assert "Page 1" in result
        assert "Page 2" in result
        assert "Page 3" in result
        assert "Test Document Title" in result

    def test_extract_single_page(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="1")

        assert "Page 1" in result
        assert "Test Document Title" in result
        assert "Page 2: Second Page" not in result

    def test_extract_page_range(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="1-2")

        assert "Page 1" in result
        assert "Page 2" in result
        assert "Page 3: Final Page" not in result

    def test_extract_multiple_pages(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="1,3")

        assert "Page 1" in result
        assert "Page 3" in result
        assert "Page 2: Second Page" not in result

    def test_file_not_found(self):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path="/nonexistent/path.pdf")

        assert "Error" in result
        assert "not found" in result


class TestExtractTables:
    def test_extract_table_markdown(self, sample_pdf_with_table):
        extract_tables = get_tool("extract_tables")
        result = extract_tables(file_path=str(sample_pdf_with_table), format="markdown")

        assert "Name" in result
        assert "Alice" in result
        assert "|" in result  # markdown table format

    def test_extract_table_csv(self, sample_pdf_with_table):
        extract_tables = get_tool("extract_tables")
        result = extract_tables(file_path=str(sample_pdf_with_table), format="csv")

        assert "Name" in result
        assert "Alice" in result

    def test_extract_table_json(self, sample_pdf_with_table):
        extract_tables = get_tool("extract_tables")
        result = extract_tables(file_path=str(sample_pdf_with_table), format="json")

        assert "Name" in result
        assert "Alice" in result

    def test_no_tables(self, sample_pdf):
        extract_tables = get_tool("extract_tables")
        result = extract_tables(file_path=str(sample_pdf))

        assert "No tables found" in result

    def test_file_not_found(self):
        extract_tables = get_tool("extract_tables")
        result = extract_tables(file_path="/nonexistent/path.pdf")

        assert "Error" in result


class TestGetMetadata:
    def test_get_metadata(self, sample_pdf):
        get_metadata = get_tool("get_metadata")
        result = get_metadata(file_path=str(sample_pdf))

        assert "Page Count: 3" in result
        assert "Producer:" in result or "Creator:" in result

    def test_file_not_found(self):
        get_metadata = get_tool("get_metadata")
        result = get_metadata(file_path="/nonexistent/path.pdf")

        assert "Error" in result


class TestGetPageCount:
    def test_get_page_count(self, sample_pdf):
        get_page_count = get_tool("get_page_count")
        result = get_page_count(file_path=str(sample_pdf))

        assert result == 3

    def test_file_not_found(self):
        get_page_count = get_tool("get_page_count")

        with pytest.raises(FileNotFoundError):
            get_page_count(file_path="/nonexistent/path.pdf")


class TestSplitPdf:
    def test_split_all_pages(self, sample_pdf, output_dir):
        split_pdf = get_tool("split_pdf")
        result = split_pdf(file_path=str(sample_pdf), output_dir=str(output_dir))

        assert "Created 3 files" in result
        assert (output_dir / "sample_page_1.pdf").exists()
        assert (output_dir / "sample_page_2.pdf").exists()
        assert (output_dir / "sample_page_3.pdf").exists()

    def test_split_specific_pages(self, sample_pdf, output_dir):
        split_pdf = get_tool("split_pdf")
        result = split_pdf(file_path=str(sample_pdf), output_dir=str(output_dir), pages="1,3")

        assert "Created 2 files" in result
        assert (output_dir / "sample_page_1.pdf").exists()
        assert not (output_dir / "sample_page_2.pdf").exists()
        assert (output_dir / "sample_page_3.pdf").exists()

    def test_file_not_found(self, output_dir):
        split_pdf = get_tool("split_pdf")
        result = split_pdf(file_path="/nonexistent/path.pdf", output_dir=str(output_dir))

        assert "Error" in result


class TestMergePdfs:
    def test_merge_pdfs(self, sample_pdf, output_dir):
        # First split, then merge
        split_pdf = get_tool("split_pdf")
        split_pdf(file_path=str(sample_pdf), output_dir=str(output_dir))

        merge_pdfs = get_tool("merge_pdfs")
        merged_path = output_dir / "merged.pdf"
        result = merge_pdfs(
            file_paths=[
                str(output_dir / "sample_page_1.pdf"),
                str(output_dir / "sample_page_2.pdf"),
            ],
            output_path=str(merged_path),
        )

        assert "Merged 2 files" in result
        assert merged_path.exists()

        # Verify merged PDF has 2 pages
        get_page_count = get_tool("get_page_count")
        assert get_page_count(file_path=str(merged_path)) == 2

    def test_file_not_found(self, output_dir):
        merge_pdfs = get_tool("merge_pdfs")
        result = merge_pdfs(
            file_paths=["/nonexistent/path1.pdf", "/nonexistent/path2.pdf"],
            output_path=str(output_dir / "merged.pdf"),
        )

        assert "Error" in result


class TestRotatePages:
    def test_rotate_all_pages(self, sample_pdf, output_dir):
        rotate_pages = get_tool("rotate_pages")
        output_path = output_dir / "rotated.pdf"
        result = rotate_pages(
            file_path=str(sample_pdf),
            rotation=90,
            output_path=str(output_path),
        )

        assert "Rotated pages by 90°" in result
        assert output_path.exists()

    def test_rotate_specific_pages(self, sample_pdf, output_dir):
        rotate_pages = get_tool("rotate_pages")
        output_path = output_dir / "rotated.pdf"
        result = rotate_pages(
            file_path=str(sample_pdf),
            rotation=180,
            pages="1,2",
            output_path=str(output_path),
        )

        assert "Rotated pages by 180°" in result
        assert output_path.exists()

    def test_invalid_rotation(self, sample_pdf, output_dir):
        rotate_pages = get_tool("rotate_pages")
        result = rotate_pages(
            file_path=str(sample_pdf),
            rotation=45,  # Invalid
            output_path=str(output_dir / "rotated.pdf"),
        )

        assert "Error" in result
        assert "90, 180, or 270" in result

    def test_file_not_found(self, output_dir):
        rotate_pages = get_tool("rotate_pages")
        result = rotate_pages(
            file_path="/nonexistent/path.pdf",
            rotation=90,
            output_path=str(output_dir / "rotated.pdf"),
        )

        assert "Error" in result


class TestExtractPages:
    def test_extract_single_page(self, sample_pdf, output_dir):
        extract_pages = get_tool("extract_pages")
        output_path = output_dir / "extracted.pdf"
        result = extract_pages(
            file_path=str(sample_pdf),
            pages="2",
            output_path=str(output_path),
        )

        assert "Extracted 1 pages" in result
        assert output_path.exists()

        # Verify content
        get_page_count = get_tool("get_page_count")
        assert get_page_count(file_path=str(output_path)) == 1

    def test_extract_page_range(self, sample_pdf, output_dir):
        extract_pages = get_tool("extract_pages")
        output_path = output_dir / "extracted.pdf"
        result = extract_pages(
            file_path=str(sample_pdf),
            pages="1-2",
            output_path=str(output_path),
        )

        assert "Extracted 2 pages" in result
        assert output_path.exists()

        get_page_count = get_tool("get_page_count")
        assert get_page_count(file_path=str(output_path)) == 2

    def test_file_not_found(self, output_dir):
        extract_pages = get_tool("extract_pages")
        result = extract_pages(
            file_path="/nonexistent/path.pdf",
            pages="1",
            output_path=str(output_dir / "extracted.pdf"),
        )

        assert "Error" in result


class TestPageRangeParsing:
    """Test the page range parsing functionality."""

    def test_single_page(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="2")

        assert "Page 2" in result
        assert "Page 1:" not in result or "--- Page 1 ---" not in result

    def test_range_from_start(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="-2")

        assert "--- Page 1 ---" in result
        assert "--- Page 2 ---" in result
        assert "--- Page 3 ---" not in result

    def test_range_to_end(self, sample_pdf):
        extract_text = get_tool("extract_text")
        result = extract_text(file_path=str(sample_pdf), pages="2-")

        assert "--- Page 1 ---" not in result
        assert "--- Page 2 ---" in result
        assert "--- Page 3 ---" in result
