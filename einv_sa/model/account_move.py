#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import qrcode
import base64
from io import BytesIO
import re
from base64 import b64encode, b64decode
import binascii

class AccountMove(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"
#_______________________________________________________________________________
    einv_amount_sale_total = fields.Monetary(string="Amount sale total", compute="_compute_total", store='True',
                                             help="")
    einv_amount_discount_total = fields.Monetary(string="Amount discount total", compute="_compute_total", store='True',
                                                 help="")
    einv_amount_tax_total = fields.Monetary(string="Amount tax total", compute="_compute_total", store='True', help="")

    @api.depends('invoice_line_ids', 'amount_total')
    def _compute_total(self):
        for r in self:
            r.einv_amount_sale_total = r.amount_untaxed + sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_discount_total = sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_tax_total = sum(line.einv_amount_tax for line in r.invoice_line_ids)

    def is_arabic(self,name):
        str_utf8 = name.encode('utf-8')
        hex_str = str_utf8.hex()
        hex_lenth = len(hex_str)
        name_lenth = len(name)
        print('str_utf8', str_utf8)
        print('hex_str', hex_str)
        print('hex_lenth', hex_lenth)
        print('name_lenth=', name_lenth)
        qwe = (name)
        print('qwe=', qwe)
        if hex_lenth/2 != name_lenth:
            print('yes is arabic ')
            return True
        else:
            print("NO it's english")
            return False

    def get_qr_code_data_m(self):
        for rec in self:
            print('GG'*15)
            if rec.type in ('out_invoice'):
                # print('type=' , rec.type)
                # print('out invoice' * 10)
                len_of_seller = 0
                sellername = str(rec.company_id.name)
                str_seller = sellername.encode('utf-8')
                hex_str = str_seller.hex()
                if self.is_arabic(sellername):
                    len_of_seller = int(len(hex_str)/2)
                    print(len_of_seller)
                else:
                    len_of_seller = len(sellername)
                print('hex_str name=', hex_str)
                seller_tag = 1
                hex_tag = hex(seller_tag)
                hex_int = hex(len_of_seller)
                # print('seller lenghth',len_of_seller)
                # print('len seller hex',len(hex_str))
                if len_of_seller < 16:
                    hex_int = '0' + hex_int[2:]
                if seller_tag < 16:
                    hex_tag = '0' + hex_tag[2:]
                total_for_seller = hex_tag + hex_int + hex_str
                # print('total for seller', total_for_seller)
                # print('*'*20)
                # ___________________________________________________________________________
                seller_vat_no = rec.company_id.vat or ''
                # print('vat num=', seller_vat_no)
                str_vat = seller_vat_no.encode('utf-8')
                hex_str2 = str_vat.hex()
                # print('hex_str==', hex_str2)
                seller_vat = 2
                hex_tag2 = hex(seller_vat)
                len_of_vat = len(seller_vat_no)
                # print('len==', len_of_vat)
                hex_int2 = hex(len_of_vat)
                if len_of_vat < 16:
                    hex_int2 = '0' + hex_int2[2:]
                if seller_vat < 16:
                    hex_tag2 = '0' + hex_tag2[2:]
                total_for_vat = hex_tag2 + hex_int2 + hex_str2
                # print('total for vat', total_for_vat)
                # print('/'*20)
                # ___________________________________________________________________________
            else:
                # print('in else'*3)
                # print('else type=', rec.type)
                # sellername = str(rec.partner_id.name)
                sellername = str(rec.company_id.name)
                # print('sellername=', sellername)
                # print('covert string to hexadecimal' * 1)
                str_seller = sellername.encode('utf-8')
                # print('str=', str_seller)
                hex_str = str_seller.hex()
                # print('hex_str=', hex_str)
                seller_tag = 1
                hex_tag = hex(seller_tag)
                len_of_seller = 0
                if self.is_arabic(sellername):
                    len_of_seller = int(len(hex_str)/2)
                    # print(len_of_seller)
                else:
                    len_of_seller = len(sellername)
                # print('len=', len_of_seller)
                hex_int = hex(len_of_seller)
                if len_of_seller < 16:
                    hex_int = '0' + hex_int[2:]
                if seller_tag < 16:
                    hex_tag = '0' + hex_tag[2:]
                total_for_seller = hex_tag + hex_int + hex_str
                # print('total for seller', total_for_seller)
                # print('*' * 20)
                # ___________________________________________________________________________
                # seller_vat_no = rec.partner_id.vat or 'False'
                seller_vat_no = self.company_id.vat or ''
                # print('seller_vat_no=', seller_vat_no)
                # print('vat num11=', seller_vat_no)
                if seller_vat_no == 'False':
                    str_vat = ''.encode('utf-8')
                else:
                    str_vat = seller_vat_no.encode('utf-8')
                hex_str2 = str_vat.hex()
                # print('hex_str==', hex_str2)
                seller_vat = 2
                hex_tag2 = hex(seller_vat)
                len_of_vat = len(seller_vat_no)
                # print('len==', len_of_vat)
                hex_int2 = hex(len_of_vat)
                if len_of_vat < 16:
                    hex_int2 = '0' + hex_int2[2:]
                if seller_vat < 16:
                    hex_tag2 = '0' + hex_tag2[2:]
                total_for_vat = hex_tag2 + hex_int2 + hex_str2
                # print('total for vat', total_for_vat)
                # print('/'*20)
            # ___________________________________________________________________________
            date = str(self.date_invoice) if self.date_invoice else str(self.create_date.date())
            # print('date', date)
            # ___________________________________________________________________________
            str_date = date.encode('utf-8')
            hex_str3 = str_date.hex()
            # print('hex_str==', hex_str3)
            tag_date = 3
            hex_tag3 = hex(tag_date)
            len_of_date = len(date)
            # print('len==', len_of_date)
            hex_int3 = hex(len_of_date)
            if len_of_date < 16:
                hex_int3 = '0' + hex_int3[2:]
            if tag_date < 16:
                hex_tag3 = '0' + hex_tag3[2:]
            total_for_date = hex_tag3 + hex_int3 + hex_str3
            # print('total for date', total_for_date)
            # print('d' * 20)
            # ___________________________________________________________________________
            amount_total_value = str(round(self.amount_total, 2))
            # print('am=', amount_total_value)
            str_date2 = amount_total_value.encode('utf-8')
            hex_str4 = str_date2.hex()
            # print('hex_str==', hex_str4)
            tag_amount_total_value = 4
            hex_tag4 = hex(tag_amount_total_value)
            len_of_amount = len(amount_total_value)
            # print('len==', len_of_amount)
            hex_int4 = hex(len_of_amount)
            if len_of_amount < 16:
                hex_int4 = '0' + hex_int4[2:]
            if tag_amount_total_value < 16:
                hex_tag4 = '0' + hex_tag4[2:]
            total_for_t = hex_tag4 + hex_int4 + hex_str4
            # print('total for t', total_for_t)
            # print('t' * 20)
            # ___________________________________________________________________________
            amount_total_tax = str(round(self.amount_tax, 2))
            # print('tx=', amount_total_tax)
            str_tax = amount_total_tax.encode('utf-8')
            hex_str5 = str_tax.hex()
            # print('hex_str==', hex_str5)
            tag_tax = 5
            hex_tag5 = hex(tag_tax)
            len_of_tax = len(amount_total_tax)
            # print('len==', len_of_tax)
            hex_int5 = hex(len_of_tax)
            if len_of_tax < 16:
                hex_int5 = '0' + hex_int5[2:]
            if tag_tax < 16:
                hex_tag5 = '0' + hex_tag5[2:]
            total_for_tax = hex_tag5 + hex_int5 + hex_str5
            # print('total for tax', total_for_tax)
            # final hex
            final_total_hex = total_for_seller + total_for_vat + total_for_date + total_for_t + total_for_tax
            # final_total_hex_str = str(total_for_seller) + str(total_for_vat) + str(total_for_date) + str(total_for_t) + str(total_for_tax)
            # print('final_total_hex', final_total_hex)
            len1 = final_total_hex[2:4]
            # print('len1=', len1)
            if len1 == '0x':
                # print('if'*9)
                hex_string = final_total_hex[0:2] + final_total_hex[4:]
                # print('len33=',hex_string)
            else:
                pp = re.sub("0x", "", final_total_hex)
                hex_string = pp
            # convert to Base64
            qr_code = b64encode(bytes.fromhex(hex_string)).decode()
            # print('final_base:=', qr_code)
            return qr_code

    qr_code = fields.Binary(string="QR Code", attachment=True, store=True)

    @api.onchange('invoice_line_ids.product_id')
    def generate_qr_code2_m(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_qr_code_data_m())
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
#_______________________________________________________________________________

class AccountMoveLine(models.Model):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    einv_amount_discount = fields.Monetary(string="Amount discount", compute="_compute_amount_discount", store='True',
                                           help="")
    einv_amount_tax = fields.Monetary(string="Amount tax", compute="_compute_amount_tax", store='True', help="")

    @api.depends('discount', 'quantity', 'price_unit')
    def _compute_amount_discount(self):
        for r in self:
            r.einv_amount_discount = r.quantity * r.price_unit * (r.discount / 100)

    @api.depends('invoice_line_tax_ids', 'discount', 'quantity', 'price_unit')
    def _compute_amount_tax(self):
        for r in self:
            r.einv_amount_tax = sum(r.price_subtotal * (tax.amount / 100) for tax in r.invoice_line_tax_ids)
