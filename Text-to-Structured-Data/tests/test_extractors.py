import unittest
from unittest.mock import patch, MagicMock
import json
from src.extractors import extract_text_from_txt, extract_text_from_docx, extract_text_from_xlsx

class TestExtractors(unittest.TestCase):

    @patch('src.extractors.open', new_callable=MagicMock)
    def test_extract_text_from_txt(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = "cliente: John Doe\nmonto: 1000\nfecha: 2023-01-01\ntipo_solicitud: loan"
        result = extract_text_from_txt('dummy.txt')
        expected = {
            "cliente": "John Doe",
            "monto": 1000,
            "fecha": "2023-01-01",
            "tipo_solicitud": "loan"
        }
        self.assertEqual(result, expected)

    @patch('src.extractors.Document')
    def test_extract_text_from_docx(self, mock_document):
        mock_doc = MagicMock()
        mock_doc.paragraphs = [MagicMock(text="cliente: Jane Doe"), MagicMock(text="monto: 2000"), MagicMock(text="fecha: 2023-02-01"), MagicMock(text="tipo_solicitud: credit")]
        mock_document.return_value = mock_doc

        with patch('src.extractors.Document', mock_document):
            result = extract_text_from_docx('dummy.docx')
            expected = {
                "cliente": "Jane Doe",
                "monto": 2000,
                "fecha": "2023-02-01",
                "tipo_solicitud": "credit"
            }
            self.assertEqual(result, expected)

    @patch('pandas.read_excel')
    def test_extract_text_from_xlsx(self, mock_read_excel):
        mock_df = MagicMock()
        mock_df.to_dict.return_value = {'cliente': 'Alice', 'monto': 3000, 'fecha': '2023-03-01', 'tipo_solicitud': 'mortgage'}
        mock_read_excel.return_value = mock_df

        result = extract_text_from_xlsx('dummy.xlsx')
        expected = {
            "cliente": "Alice",
            "monto": 3000,
            "fecha": "2023-03-01",
            "tipo_solicitud": "mortgage"
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()