from odoo import api, models


class FollowupLine(models.Model):
    _inherit = "account_followup.followup.line"

    @api.model
    def _magyc_setup_dunning(self):
        """Create the three MAGYC reminder levels once per company."""
        levels = [
            (0, "magyc_documents.tpl_reminder_1"),
            (7, "magyc_documents.tpl_reminder_2"),
            (12, "magyc_documents.tpl_reminder_3"),
        ]
        templates = self.env["mail.template"].browse()
        for _delay, xmlid in levels:
            template = self.env.ref(xmlid, raise_if_not_found=False)
            if template:
                templates |= template
        if not templates:
            return False
        # The stock reminder levels (7/15/30 days) collide with the MAGYC delays;
        # replace them with the three MAGYC levels.
        stale = self.search([
            ("company_id", "=", self.env.company.id),
            ("mail_template_id", "not in", templates.ids),
        ])
        stale.unlink()

        for delay, xmlid in levels:
            template = self.env.ref(xmlid, raise_if_not_found=False)
            if not template:
                continue
            existing = self.search([
                ("company_id", "=", self.env.company.id),
                ("mail_template_id", "=", template.id),
            ], limit=1)
            if existing:
                existing.write({"delay": delay})
                continue
            self.create({
                "delay": delay,
                "company_id": self.env.company.id,
                "send_email": True,
                "mail_template_id": template.id,
            })
        return True
