from markdown_pdf import MarkdownPdf, Section

pdf = MarkdownPdf(toc_level=2)
pdf.add_section(Section("# Title\nThis is a **test**."))
pdf.save("test.pdf")
print("PDF created successfully!")
