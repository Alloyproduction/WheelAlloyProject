# -*- coding: utf-8 -*-
from odoo.addons.sale.controllers.portal import CustomerPortal  # Import the class
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper


class CustomerPortalController(CustomerPortal):  # Inherit in your custom class

    # @http.route('/sales/sale_quotation_onboarding_panel', auth='user', type='json')
    # def sale_quotation_onboarding(self):
    #     res = super(CustomOnboardingController, self).sale_quotation_onboarding()
    #     # Your code goes here
    #     return res


    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, res_id, access_token=None, partner_name=None, signature=None, order_id=None):
        try:
            order_sudo = self._document_check_access('sale.order', res_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order')}

        if not order_sudo.has_to_be_signed():
            if order_sudo.opportunity_id:
                won = http.request.env['crm.stage'].search([('name','=','Won')])
                order_sudo.opportunity_id.write({
                    'stage_id': won.id
                })
                # print(">>>>>>>>>", order_sudo.opportunity_id.name)
            # return {'error': _('HHHHHHHHHHHHHHHHHHHHHHHHHHH')}
        if not signature:
            return {'error': _('Signature is missing.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm_replica()

        order_sudo.signature = signature
        order_sudo.signed_by = partner_name

        pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([order_sudo.id])[0]
        _message_post_helper(
            res_model='sale.order',
            res_id=order_sudo.id,
            message=_('Order signed by %s') % (partner_name,),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string='&message=sign_ok'),
        }

    @http.route(['/my/orders/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper(message=message, res_id=order_id, res_model='sale.order', **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"
        # print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        # lost = http.request.env['crm.stage'].search([('name','=','Lost')])
        # print(lost)
        # print(lost.name)
        order_sudo.opportunity_id.action_set_lost()
        # print(">>>>>>>>>", order_sudo.opportunity_id.name)
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))
