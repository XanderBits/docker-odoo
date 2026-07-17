from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tools import mute_logger
from psycopg2.errors import CheckViolation, UniqueViolation
import logging

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestFiscalProfileWithholding(AccountTestInvoicingCommon):
    """Valida facturas con y sin retención, incluyendo casos límite
    (cliente sin perfil fiscal, o sin regla asociada)."""

    def setUp(self):
        super().setUp()
        self.WithholdingRule = self.env['withholding.rule']
        self.AccountMove = self.env['account.move']

        # Regla solo para 'withholding_agent' (el perfil 'standard' queda sin regla)
        self.rule = self.WithholdingRule.create({
            'name': 'Retención agente 75%',
            'fiscal_profile': 'withholding_agent',
            'withholding_percentage': 75,
        })

        # partner_a -> perfil con regla | partner_b -> perfil sin regla
        self.partner_a.fiscal_profile = 'withholding_agent'
        self.partner_b.fiscal_profile = 'standard'
        self.partner_no_profile = self.env['res.partner'].create({
            'name': 'Cliente sin perfil fiscal'
        })

    def create_invoice(self, partner):
        invoice = self._create_invoice(
            move_type='out_invoice',
            partner_id=partner.id,
            invoice_line_ids=[
                self._prepare_invoice_line(price_unit=1000, tax_ids=[])
            ]
        )
        return invoice

    def test_withholding_applied_agent_profile(self):
        _logger.info("*" * 20 + " RETENCION APLICADA (AGENTE) " + "*" * 20)
        invoice = self.create_invoice(self.partner_a)

        self.assertEqual(invoice.partner_id.fiscal_profile, 'withholding_agent')
        self.assertEqual(invoice.amount_untaxed, 1000)

        invoice.action_post()

        # base 1000 * 75% = 750
        _logger.info(f"MONTO DE RETENCIÓN: {invoice.withholding_amount}")
        self.assertEqual(invoice.withholding_amount, 750)

    def test_no_withholding_without_profile(self):
        invoice = self.create_invoice(self.partner_no_profile)

        self.assertFalse(invoice.partner_id.fiscal_profile)

        invoice.action_post()

        self.assertEqual(invoice.withholding_amount, 0)

    def test_no_withholding_without_rule(self):
        invoice = self.create_invoice(self.partner_b)

        self.assertEqual(invoice.partner_id.fiscal_profile, 'standard')

        invoice.action_post()

        self.assertEqual(invoice.withholding_amount, 0)

    def test_check_withholding_percentage(self):
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.WithholdingRule.create({
                'name': 'Retención inválida',
                'fiscal_profile': 'exempt',
                'withholding_percentage': 200,
            })

        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.WithholdingRule.create({
                'name': 'Retención inválida',
                'fiscal_profile': 'exempt',
                'withholding_percentage': -1,
            })

    def test_unique_fiscal_profile(self):
        # En setUp ya existe una regla para 'withholding_agent'
        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self.WithholdingRule.create({
                'name': 'Retención duplicada',
                'fiscal_profile': 'withholding_agent',
                'withholding_percentage': 10,
            })
