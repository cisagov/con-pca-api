"""PyPDF2 Utils."""
# Third-Party Libraries
from PyPDF2 import PdfFileWriter
from PyPDF2.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    createStringObject,
)


def append_attachment(writer: PdfFileWriter, fname: str, fdata: bytes):
    """Append attachments to a PDF."""
    # The entry for the file
    file_entry = DecodedStreamObject()
    file_entry.setData(fdata)
    file_entry.update({NameObject("/Type"): NameObject("/EmbeddedFile")})

    # The Filespec entry
    ef_entry = DictionaryObject()
    ef_entry.update({NameObject("/F"): file_entry})

    filespec = DictionaryObject()
    filespec.update(
        {
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/F"): createStringObject(fname),
            NameObject("/EF"): ef_entry,
        }
    )

    if "/Names" not in writer._root_object.keys():
        # No files attached yet. Create the entry for the root, as it needs a reference to the Filespec
        embedded_filenames_dict = DictionaryObject()
        embedded_filenames_dict.update(
            {NameObject("/Names"): ArrayObject([createStringObject(fname), filespec])}
        )

        embedded_files_dict = DictionaryObject()
        embedded_files_dict.update(
            {NameObject("/EmbeddedFiles"): embedded_filenames_dict}
        )
        writer._root_object.update({NameObject("/Names"): embedded_files_dict})
    else:
        # There are files already attached. Append the new file.
        writer._root_object["/Names"]["/EmbeddedFiles"]["/Names"].append(
            createStringObject(fname)
        )
        writer._root_object["/Names"]["/EmbeddedFiles"]["/Names"].append(filespec)
