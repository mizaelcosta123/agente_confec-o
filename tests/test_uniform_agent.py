import tempfile
import unittest
from pathlib import Path

from src.uniform_agent import (
    UniformBriefing,
    build_prompt,
    encode_logo_as_data_url,
    generate_local_mock_response,
    is_quota_error,
)


class UniformAgentTests(unittest.TestCase):
    def setUp(self):
        self.briefing = UniformBriefing(
            segmento="Industrial",
            objetivo_visual="Visual técnico",
            publico_uso="Equipe manutenção",
            restricoes="Alta legibilidade",
            cor_nome="Azul Marinho (#001F3F)",
            cor_hex="#001F3F",
            logo_proporcao="12x8 cm",
            tamanho_mockup="TBU",
            modelo_peca="Camisa Polo",
            metodo_aplicacao="Silk",
        )

    def test_build_prompt_contains_required_sections(self):
        prompt = build_prompt(self.briefing)
        self.assertIn("Pedido de criação de mockup de uniforme", prompt)
        self.assertIn("Instruções obrigatórias", prompt)
        self.assertIn("Código HEX extraído: #001F3F", prompt)

    def test_local_response_is_structured(self):
        response = generate_local_mock_response(self.briefing)
        self.assertIn("A) Resumo do pedido interpretado", response)
        self.assertIn("B) Proposta de design", response)
        self.assertIn("E) Próximo passo", response)

    def test_quota_error_detection(self):
        exc = Exception("Error code: 429 - {'code':'insufficient_quota'}")
        self.assertTrue(is_quota_error(exc))

    def test_encode_logo_png_data_url(self):
        with tempfile.TemporaryDirectory() as td:
            logo = Path(td) / "logo.png"
            logo.write_bytes(b"fake-png-content")
            data_url = encode_logo_as_data_url(str(logo))

        self.assertTrue(data_url.startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
