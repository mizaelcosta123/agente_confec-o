import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.uniform_agent import (
    UniformBriefing,
    build_creation_prompt,
    encode_logo_inline_part,
    generate_local_mock_response,
    validate_gemini_key,
)


class UniformAgentTests(unittest.TestCase):
    def setUp(self):
        self.briefing = UniformBriefing(
            segmento="Industrial",
            cores="Azul e amarelo",
            detalhes="Logo no peito esquerdo",
            cor_hex="#1E73BE",
            logo_proporcao="12x8 cm",
            tamanho_mockup="TBU",
            tamanho_camiseta="G",
            modelo_camiseta="Polo",
            aplicacao_lado="Frente e Verso",
            modelagem="Regular",
            tecnica_impressao="Sublimação",
        )

    def test_build_prompt_contains_required_sections(self):
        prompt = build_creation_prompt(self.briefing)
        self.assertIn("Modelo da camiseta: Polo", prompt)
        self.assertIn("Aplicação da arte: Frente e Verso", prompt)
        self.assertIn("NUNCA alterar a logo anexada", prompt)

    def test_local_response_is_structured(self):
        response = generate_local_mock_response(self.briefing)
        self.assertIn("A) Resumo do pedido interpretado", response)
        self.assertIn("C) Regra da logo", response)
        self.assertIn("Logo original preservada", response)

    def test_validate_key_rejects_invalid_prefix(self):
        ok, msg, models = validate_gemini_key("sk-test")
        self.assertFalse(ok)
        self.assertIn("Formato inválido", msg)
        self.assertEqual(models, [])

    @patch("src.uniform_agent.list_gemini_models", return_value=["gemini-1.5-flash", "gemini-1.5-pro"])
    def test_validate_key_accepts_valid_and_active(self, _mock_models):
        ok, msg, models = validate_gemini_key("AIzaTESTE123456")
        self.assertTrue(ok)
        self.assertIn("válida e ativa", msg)
        self.assertGreaterEqual(len(models), 1)

    def test_encode_logo_png_inline_part(self):
        with tempfile.TemporaryDirectory() as td:
            logo = Path(td) / "logo.png"
            logo.write_bytes(b"fake-png-content")
            part = encode_logo_inline_part(str(logo))

        self.assertIn("inline_data", part)
        self.assertEqual(part["inline_data"]["mime_type"], "image/png")
        self.assertTrue(len(part["inline_data"]["data"]) > 10)


if __name__ == "__main__":
    unittest.main()
