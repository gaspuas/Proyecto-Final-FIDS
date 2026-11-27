import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MigracionTokenTests(unittest.TestCase):
    def test_migracion_define_token_hash_y_revocacion(self):
        sql = (ROOT / 'database/migraciones/004_sesiones_token.sql').read_text(encoding='utf-8')
        self.assertIn('token_hash CHAR(64)', sql)
        self.assertIn('expira_en DATETIME(6)', sql)
        self.assertIn('revocado_en DATETIME(6)', sql)
        self.assertIn('ON DELETE CASCADE', sql)


if __name__ == '__main__':
    unittest.main()
