from odoo import models


# Creating Excel Report
class PatientCardXLS(models.AbstractModel):
    _name = 'report.hospital.report_patient_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, line):
        c = 0
        for lines in line:
            c += 1
            format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
            format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
            sheet = workbook.add_worksheet('Patient Card %s' % (c))

            sheet.right_to_left()

            sheet.set_column(3, 3, 50)
            sheet.set_column(2, 2, 30)
            sheet.write(2, 2, 'Name', format1)
            sheet.write(2, 3, lines.patient_name, format2)
            sheet.write(3, 2, 'Age', format1)
            sheet.write(3, 3, lines.patient_age, format2)
