# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import operator
import urllib
import urllib2
import cookielib
import copy

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters  # noqa


from django.contrib.auth import authenticate, login

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon.utils import memoized
from horizon import views

from openstack_dashboard import api
from openstack_dashboard import policy



from openstack_dashboard.dashboards.identity.users \
    import forms as project_forms
from openstack_dashboard.dashboards.identity.users \
    import tables as project_tables


class IndexView(tables.DataTableView):
    table_class = project_tables.UsersTable
    template_name = 'identity/users/index.html'
    page_title = _("Users")

    def get_data(self):
        users = []
        domain_context = self.request.session.get('domain_context', None)
        if policy.check((("identity", "identity:list_users"),),
                        self.request):
            try:
                users = api.keystone.user_list(self.request,
                                               domain=domain_context)
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user list.'))
        elif policy.check((("identity", "identity:get_user"),),
                          self.request):
            try:
                user = api.keystone.user_get(self.request,
                                             self.request.user.id)
                users.append(user)
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user information.'))
        else:
            msg = _("Insufficient privilege level to view user information.")
            messages.info(self.request, msg)
        return users


class UpdateView(forms.ModalFormView):
    template_name = 'identity/users/update.html'
    modal_header = _("Update User")
    form_id = "update_user_form"
    form_class = project_forms.UpdateUserForm
    submit_label = _("Update User")
    submit_url = "horizon:identity:users:update"
    success_url = reverse_lazy('horizon:identity:users:index')
    page_title = _("Update User")

    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.keystone.user_get(self.request, self.kwargs['user_id'],
                                         admin=True)
        except Exception:
            redirect = reverse("horizon:identity:users:index")
            exceptions.handle(self.request,
                              _('Unable to retrieve user information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.kwargs['user_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        user = self.get_object()
        domain_id = getattr(user, "domain_id", None)
        domain_name = ''
        # Retrieve the domain name where the project belong
        if api.keystone.VERSIONS.active >= 3:
            try:
                domain = api.keystone.domain_get(self.request,
                                                 domain_id)
                domain_name = domain.name
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve project domain.'))
        return {'domain_id': domain_id,
                'domain_name': domain_name,
                'id': user.id,
                'name': user.name,
                'project': user.project_id,
                'email': getattr(user, 'email', None)}



class CreateView(forms.ModalFormView):

    template_name = 'identity/users/create.html'
    modal_header = _("Create User")
    form_id = "create_user_form"
    form_class = project_forms.CreateUserForm
    submit_label = _("Create User")
    submit_url = reverse_lazy("horizon:identity:users:create")
    success_url = reverse_lazy('horizon:identity:users:index')
    page_title = _("Create User")

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        try:
            roles = api.keystone.role_list(self.request)
        except Exception:
            redirect = reverse("horizon:identity:users:index")
            exceptions.handle(self.request,
                              _("Unable to retrieve user roles."),
                              redirect=redirect)
        roles.sort(key=operator.attrgetter("id"))
        kwargs['roles'] = roles
        print "#######################################"
        print roles[0].id
        print "#######################################"
        return kwargs

    def get_initial(self):
        # Set the domain of the user
        domain = api.keystone.get_default_domain(self.request)
        default_role = api.keystone.get_default_role(self.request)
        print(default_role)
        print("#################")
        return {'domain_id': domain.id,
                'domain_name': domain.name,
                'role_id': getattr(default_role, "id", None)}



class CreateOutsideView(forms.ModalFormView):

    template_name = 'auth/create_user.html'
    modal_header = _("Create User")
    form_id = "create_user_form"
    form_class = project_forms.OutsideCreateUserForm
    submit_label = _("Create User")
    submit_url = "/auth/create_user/"
    success_url = "/auth/login"
    page_title = _("Create User")

    def dispatch(self, *args, **kwargs):
        return super(CreateOutsideView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateOutsideView, self).get_form_kwargs()

        kwargs['roles'] = ['8b2a8e6f8db24a268b275c646903f263', '8b2a8e6f8db24a268b275c646903f263']
        return kwargs

    def get_initial(self):
        # Set the domain of the user
        # domain = api.keystone.get_default_domain(self.request)
        # default_role = api.keystone.get_default_role(self.request)
        # print(default_role)
        # print("#################")
        return None

# class Login(object):
#
#     def __init__(self):
#
#     def dispatch(self):
#         print self.request


class DetailView(views.HorizonTemplateView):
    template_name = 'identity/users/detail.html'
    page_title = _("User Details: {{ user.name }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        user = self.get_data()
        table = project_tables.UsersTable(self.request)
        domain_id = getattr(user, "domain_id", None)
        domain_name = ''
        if api.keystone.VERSIONS.active >= 3:
            try:
                domain = api.keystone.domain_get(self.request, domain_id)
                domain_name = domain.name
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve project domain.'))

        context["user"] = user
        context["domain_id"] = domain_id
        context["domain_name"] = domain_name
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(user)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            user_id = self.kwargs['user_id']
            user = api.keystone.user_get(self.request, user_id)
        except Exception:
            redirect = self.get_redirect_url()
            exceptions.handle(self.request,
                              _('Unable to retrieve user details.'),
                              redirect=redirect)
        return user

    def get_redirect_url(self):
        return reverse('horizon:identity:users:index')


class ChangePasswordView(forms.ModalFormView):
    template_name = 'identity/users/change_password.html'
    modal_header = _("Change Password")
    form_id = "change_user_password_form"
    form_class = project_forms.ChangePasswordForm
    submit_url = "horizon:identity:users:change_password"
    submit_label = _("Save")
    success_url = reverse_lazy('horizon:identity:users:index')
    page_title = _("Change Password")

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.keystone.user_get(self.request, self.kwargs['user_id'],
                                         admin=True)
        except Exception:
            redirect = reverse("horizon:identity:users:index")
            exceptions.handle(self.request,
                              _('Unable to retrieve user information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        args = (self.kwargs['user_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        user = self.get_object()
        return {'id': self.kwargs['user_id'],
                'name': user.name}
