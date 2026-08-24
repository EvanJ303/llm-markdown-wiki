def guide() -> str:
	"""Describe the wiki tools and their path and file-type restrictions."""
	return (
		'Use read and search to inspect the wiki. Use write to create or replace '
		'allowed document types, append to add content to an existing allowed '
		'text document, edit to replace text in an allowed document, and delete '
		'to remove a document. File paths must be inside the wiki directory.'
	)
