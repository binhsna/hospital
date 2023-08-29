from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import re


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # Định nghĩa lại hàm của lớp cơ sở
    @api.multi
    def action_confirm(self):
        print("odoo mates")
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    patient_name = fields.Char(string='Patient Name')
    is_patient = fields.Boolean(string='Is Patient')


class ResPartner(models.Model):
    _inherit = 'res.partner'
    # Thêm giá trị mới vào trường lựa chọn Odoo
    company_type = fields.Selection(selection_add=[('obi', 'Odoo Binh'), ('odoodev', 'Odoo Dev')])

    @api.model
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        print("Yes working")
        # do the custom coding here
        return res


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Patient Record'
    _rec_name = 'patient_name'

    # How To Call Python Function From Menu Item in Odoo
    def action_patients(self):
        print("Odoo Mates..............")
        return {
            'name': _('Patients Server Action'),
            'domain': [],
            'view_type': 'form',
            'res_model': 'hospital.patient',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    # In ra file .pdf
    @api.multi
    def print_report(self):
        return self.env.ref('hospital.report_patient_card').report_action(self)

    # In ra file .xlsx
    @api.multi
    def print_report_excel(self):
        return self.env.ref('hospital.report_patient_card_xlx').report_action(self)

    # Kiểm tra tuổi nhập vào
    @api.constrains('patient_age')
    def check_age(self):
        for rec in self:
            if rec.patient_age <= 5:
                raise ValidationError(_("The Age Must be Greater than 5"))

    @api.constrains('email_id')
    def _check_email_format(self):
        for record in self:
            if record.email_id:
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                if not re.match(pattern, record.email_id):
                    raise models.ValidationError("Địa chỉ email không hợp lệ! Vui lòng kiểm tra lại.")

    @api.constrains('phone')
    def is_valid_phone_number(self):
        for record in self:
            if record.phone:
                pattern = r'^\d{10}$'  # Mẫu chỉ chấp nhận 10 chữ số
                if not re.match(pattern, record.phone):
                    raise models.ValidationError("Số điện thoại không hợp lệ! Vui lòng kiểm tra lại.")

    # Test Create Scheduled Actions
    @api.model
    def test_cron_job(self):
        print("Test Create Scheduled Actions")
        # code accordingly to execute the cron

    # Hàm đặc biệt giúp tùy chỉnh cách hiển thị tên

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.patient_name, rec.name_seq)))
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', ('name_seq', operator, name), ('patient_name', operator, name)]
        return super(HospitalPatient, self).search(domain, limit=limit).name_get()

    # Gán nhóm tuổi phù hợp
    @api.depends('patient_age')
    def set_age_group(self):
        for rec in self:
            if rec.patient_age < 18:
                rec.age_group = 'minor'
            else:
                rec.age_group = 'major'

    # Hàm bắt sự kiện open button appointments
    @api.multi
    def open_patient_appointments(self):
        return {
            'name': _('Appointments'),
            'domain': [('patient_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_appointment_count(self):
        count = self.env['hospital.appointment'].search_count([('patient_id', '=', self.id)])
        self.appointment_count = count

    @api.onchange('doctor_id')
    def set_doctor_gender(self):
        print("Cập nhật giới tính cho doctor")
        for rec in self:
            if rec.doctor_id:
                rec.doctor_gender = rec.doctor_id.gender

    # Gủi mail
    def action_send_card(self):
        # sending the patient report to patient via email
        template_id = self.env.ref('hospital.patient_card_email_template').id
        print("Mail Template ID: ", template_id)
        template = self.env['mail.template'].browse(template_id)
        print("Template: ", template_id)
        template.send_mail(self.id, force_send=True)

    # Chuyển sang chữ in hoa
    @api.depends('patient_name')
    def _compute_upper_name(self):
        for rec in self:
            rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False

    # Chuyển ngược lại chữ in thường
    def _inverse_upper_name(self):
        for rec in self:
            rec.patient_name = rec.patient_name_upper.lower() if rec.patient_name_upper else False

    phone = fields.Char(string="Phone")
    name_seq = fields.Char(string='Patient ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female')
    ], default='male', string="Gender")
    age_group = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor')
    ], string='Age Group', compute='set_age_group', store=True)
    patient_name = fields.Char(string="Name", required=True, track_visibility='always')
    patient_age = fields.Integer('Age', track_visibility="always", group_operator=False)
    # patient_age2 = fields.Float(string="Age2")
    notes = fields.Text(string="Registration Notes", translate=True)
    image = fields.Binary(string="Image", attachment=True)
    appointment_count = fields.Integer(string="Appointment", compute='get_appointment_count')
    active = fields.Boolean("Active", default=True)
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    email_id = fields.Char(string="Email")
    user_id = fields.Many2one('res.users', string="PRO")

    doctor_gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female'),
    ], string="Doctor Gender")
    patient_name_upper = fields.Char(compute='_compute_upper_name', inverse='_inverse_upper_name')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')

            result = super(HospitalPatient, self).create(vals)
        return result
