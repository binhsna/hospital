from odoo import api, models, _


# How To Call A Python Function While Printing PDF Report in Odoo
class PatientCardReport(models.AbstractModel):
    _name = 'report.hospital.report_patient'
    _description = 'Patient card Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hospital.patient'].browse(docids[0])
        appointments = self.env['hospital.appointment'].search([('patient_id', '=', docids[0])])
        appointment_list = []
        return {
            'doc_model': 'hospital.patient',
            'docs': docs,
            'appointment_list': appointment_list,
        }
