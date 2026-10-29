def migrate(cr, version):
    """Install the MAGYC reminder levels on existing databases."""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["account_followup.followup.line"]._magyc_setup_dunning()
