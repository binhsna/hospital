import pytz
# from lxml import etree

from odoo import api, models, fields, _


# Đặt lịch khám bệnh
class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "appointment_date desc"  # _order = "id desc"

    # Odoo ORM: Thao tác RecordSet - Sắp xếp, Lọc & Ánh xạ
    def test_recordset(self):
        for rec in self:
            print("Odoo ORM: Record Set Operation")
            partners = self.env['res.partner'].search([])
            print("Mapped partners...", partners.mapped('email'))
            print(" Sorted partners...", partners.sorted(lambda o: o.write_date, reverse=True))
            print(" Filtered partners...", partners.filtered(lambda o: not o.customer))

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Appointment Confirmed... Thanks You',
                    'type': 'rainbow_man',
                }
            }

    # Phương thức gửi thông báo đến user
    def action_notify(self):
        for rec in self:
            rec.doctor_id.user_id.notify_warning(message='Appointment is Confirmed')
            print("Notifying >>>>>")

    def action_done(self):
        for rec in self:
            rec.state = 'draft'

    # Xóa bản ghi appointment_lines

    def delete_lines(self):
        for rec in self:
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
            time_in_timezone = pytz.utc.localize(rec.appointment_datetime).astimezone(user_tz)
            print("Time in UTC -->", rec.appointment_datetime)
            print("Time in Users Timezone -->", time_in_timezone)
            rec.appointment_lines = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')

        result = super(HospitalAppointment, self).create(vals)
        return result

    # Định nghĩa lại hàm write
    @api.multi
    def write(self, vals):
        # overriding the write method of appointment model
        res = super(HospitalAppointment, self).write(vals)
        print("Test write function")
        # do as per the need
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    def _get_default_patient_id(self):
        return 1

    # Phương thức đặc biệt -> Gán mặc định cho các trường dữ liệu của model khi create
    # @api.model
    # def default_get(self, fields):
    #     res = super(HospitalAppointment, self).default_get(fields)
    #     appointment_lines = []
    #     product_rec = self.env['product.product'].search([])
    #     for pro in product_rec:
    #         line = (0, 0, {
    #             'product_id': pro.id,
    #             'product_qty': 1,
    #         })
    #         appointment_lines.append(line)
    #     res.update({
    #         'appointment_lines': appointment_lines,
    #         'patient_id': 1,
    #         'notes': 'Please to note >>>'
    #     })
    #     return res

    name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_ids = fields.Many2many('hospital.doctor', 'hospital_patient_rel', 'appointment_id', 'doctor_id_rec',
                                  string='Doctors')
    patient_age = fields.Integer('Age', related='patient_id.patient_age')
    notes = fields.Text(string="Registration Note")
    doctor_note = fields.Text(string="Note", track_visibility='onchange')
    pharmacy_note = fields.Text(string="Note", track_visibility='always')
    appointment_date = fields.Date(string="Date")
    appointment_datetime = fields.Datetime(string='Date Time')
    appointment_date_end = fields.Datetime(string='Date End')
    appointment_lines = fields.One2many('hospital.appointment.lines', 'appointment_id', string='Appointment Lines')
    partner_id = fields.Many2one('res.partner', string="Customer")
    order_id = fields.Many2one('sale.order', string="Sale Order")
    # Dùng cho biểu đồ Graph
    amount = fields.Float(string="Total Amount")

    # Tạo trạng thái/thanh trạng thái cho bản ghi
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Status", readonly=True, default='draft')
    product_id = fields.Many2one('product.template', string="Product Template")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            lines = [(5, 0, 0)]  # Nếu dùng dòng này thì sẽ xóa lines cũ
            for line in self.product_id.product_variant_ids:
                vals = {
                    'product_id': line.id,
                    'product_qty': 5
                }
                lines.append((0, 0, vals))
            rec.appointment_lines = lines


# Thuốc chữa bệnh
class HospitalAppointmentLines(models.Model):
    _name = 'hospital.appointment.lines'
    _description = 'Appointment Lines'

    product_id = fields.Many2one('product.product', string='Medicine')
    product_qty = fields.Integer(string="Quantity")
    sequence = fields.Integer(string="Sequence")
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment ID')
    # display_type = fields.Selection([
    #     ('line_section', "Section"),
    #     ('line_note', "Note")
    # ], default=False, help="Technical field for UX purpose.")
