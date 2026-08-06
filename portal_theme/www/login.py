# Patched by Portal Theme pt_patcher (Patch 05)
from urllib.parse import urlparse
import frappe, frappe.utils
from frappe import _
from frappe.apps import get_default_path
from frappe.auth import LoginManager
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, get_url
from frappe.utils.data import escape_html
from frappe.utils.html_utils import get_icon_html
from frappe.utils.jinja import guess_is_path
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, redirect_post_login
from frappe.utils.password import get_decrypted_password
from frappe.website.utils import get_home_page

no_cache = True

def _get(doc, field, default=None):
    try: val = doc.get(field)
    except Exception: val = None
    if val in (None, ""): return default
    return val

def _get_website(field):
    try:
        v = frappe.db.get_single_value("Website Settings", field)
        return v or ""
    except Exception:
        return ""

def _get_default_company_name():
    try:
        c = frappe.defaults.get_global_default("company")
        if c:
            return frappe.db.get_value("Company", c, "company_name") or c
    except Exception:
        pass
    return ""

def _build_brand_login(pts, app_name):
    active = frappe.db.get_value("Portal Theme", {"is_active": 1},
        ["primary", "secondary"], as_dict=True) or {}
    brand_green = active.get("primary") or "#3ECF57"
    brand_navy  = active.get("secondary") or "#17304D"
    year = frappe.utils.now_datetime().year
    website_copyright = _get_website("copyright")
    website_powered   = _get_website("footer_powered")
    website_description = _get_website("description") or _get_website("meta_description")

    subtitle_default = _get_default_company_name() or ""
    copyright_default = f"© {year} {website_copyright}" if website_copyright else ""  # Patch 09: auto © and year
    terms_default = website_copyright or f"© {year} {app_name}. All rights reserved."
    powered_default = website_powered or ""

    return {
        "nav_use_diagonal":  int(_get(pts, "login_navbar_use_diagonal", 1) or 0),
        "nav_bg1":           _get(pts, "login_navbar", brand_green),
        "nav_bg2":           _get(pts, "login_navbar_color_2", brand_navy),
        "nav_text":          _get(pts, "login_navbar_text", "#FFFFFF"),
        "nav_right_text":    _get(pts, "login_navbar_right_text", _("Login")),
        "footer_use_diagonal": 1,
        "footer_bg1":        _get(pts, "login_footer_color", brand_green),
        "footer_bg2":        _get(pts, "login_footer_color_2", brand_navy),
        "footer_text":       _get(pts, "login_footer_text_color", "#FFFFFF"),
        "card_bg":           _get(pts, "login_card_background", "#F7F0E7"),
        "card_radius":       int(_get(pts, "login_card_border_radius", 15) or 15),
        "card_max_width":    int(_get(pts, "login_card_max_width", 400) or 400),
        "card_opacity":      float(_get(pts, "opacity_of_login_card", 1) or 1),
        "subtitle":          _get(pts, "login_subtitle", subtitle_default),
        "btn_use_diagonal":  int(_get(pts, "login_button_use_diagonal", 1) or 0),
        "btn_bg1":           _get(pts, "login_button_bg_1", brand_green),
        "btn_bg2":           _get(pts, "login_button_bg_2", brand_navy),
        "btn_text":          _get(pts, "login_button_text", "#FFFFFF"),
        "terms_text":        _get(pts, "login_terms_text", terms_default),
        "copyright_text":    _get(pts, "login_copyright_text", copyright_default),
        "powered_by_text":   _get(pts, "login_powered_by_text", powered_default),
        "powered_by_url":    _get(pts, "login_powered_by_url", ""),
        "og_description":    website_description or "",
        "show_social_icons": int(_get(pts, "login_show_social_icons", 1) or 0),
        "social": {
            "facebook":  _get(pts, "login_facebook_url", ""),
            "twitter":   _get(pts, "login_twitter_url", ""),
            "linkedin":  _get(pts, "login_linkedin_url", ""),
            "instagram": _get(pts, "login_instagram_url", ""),
        },
    }


def get_context(context):
    from frappe.integrations.frappe_providers.frappecloud_billing import get_site_login_url
    from frappe.utils.frappecloud import on_frappecloud

    redirect_to = frappe.local.request.args.get("redirect-to")
    redirect_to = sanitize_redirect(redirect_to)
    if frappe.session.user != "Guest":
        if not redirect_to:
            if frappe.session.data.user_type == "Website User":
                redirect_to = get_default_path() or get_home_page()
            else:
                redirect_to = get_default_path() or "/app"
        if redirect_to != "login":
            frappe.local.flags.redirect_location = redirect_to
            raise frappe.Redirect

    context.no_header = True
    context.for_test = "login.html"
    context["title"] = "Login"
    context["hide_login"] = True
    context["provider_logins"] = []
    context["disable_signup"] = cint(frappe.get_website_settings("disable_signup"))
    context["show_footer_on_login"] = cint(frappe.get_website_settings("show_footer_on_login"))
    context["disable_user_pass_login"] = cint(frappe.get_system_settings("disable_user_pass_login"))
    context["logo"] = get_app_logo()
    context["app_name"] = (frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or _("Framework"))

    pts = frappe.get_single("Portal Theme Setting")
    if pts.enable and pts.apply_on_login_page:
        context["background_image"] = pts.background_image
        context["background_opacity"] = pts.background_opacity
        context["text_color"] = pts.text_color
        context["completely_hide_footer_from_login_page"] = pts.completely_hide_footer_from_login_page
        context["position_of_login_card"] = pts.position_of_login_card
        context["opacity_of_login_card"] = pts.opacity_of_login_card
        context["apply_image_or_color"] = pts.apply_image_or_color
        context["background_color"] = pts.background_color
        context["login_navbar"] = pts.login_navbar
        context["login_navbar_text"] = pts.login_navbar_text
        if pts.apply_image_or_color == "Slider":
            context["background_slider_images"] = [img.image for img in pts.background_images]
            context["interval"] = pts.interval
            context["transition"] = pts.transition

    context["brand_login"] = _build_brand_login(pts, context["app_name"])

    signup_form_template = frappe.get_hooks("signup_form_template")
    if signup_form_template and len(signup_form_template):
        path = signup_form_template[-1]
        if not guess_is_path(path):
            path = frappe.get_attr(signup_form_template[-1])()
    else:
        path = "frappe/templates/signup.html"
    if path:
        context["signup_form_template"] = frappe.get_template(path).render()

    providers = frappe.get_all("Social Login Key", filters={"enable_social_login": 1},
        fields=["name","client_id","base_url","provider_name","icon"], order_by="name")
    for provider in providers:
        client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret", raise_exception=False)
        if not client_secret: continue
        icon = None
        if provider.icon:
            if provider.provider_name == "Custom":
                icon = get_icon_html(provider.icon, small=True)
            else:
                icon = f"<img src={escape_html(provider.icon)!r} alt={escape_html(provider.provider_name)!r}>"
        if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
            context.provider_logins.append({"name":provider.name,"provider_name":provider.provider_name,
                "auth_url":get_oauth2_authorize_url(provider.name, redirect_to),"icon":icon})
            context["social_login"] = True

    if cint(frappe.db.get_value("LDAP Settings", "LDAP Settings", "enabled")):
        from frappe.integrations.doctype.ldap_settings.ldap_settings import LDAPSettings
        context["ldap_settings"] = LDAPSettings.get_ldap_client_settings()

    login_label = [_("Email")]
    if frappe.utils.cint(frappe.get_system_settings("allow_login_using_mobile_number")):
        login_label.append(_("Mobile"))
    if frappe.utils.cint(frappe.get_system_settings("allow_login_using_user_name")):
        login_label.append(_("Username"))
    context["login_label"] = f" {_('or')} ".join(login_label)

    context["login_with_email_link"] = frappe.get_system_settings("login_with_email_link")
    context["login_with_frappe_cloud_url"] = (
        f"{get_site_login_url()}?site={frappe.local.site}"
        if on_frappecloud() and frappe.conf.get("fc_communication_secret") else None
    )
    return context


@frappe.whitelist(allow_guest=True)
def login_via_token(login_token: str):
    sid = frappe.cache.get_value(f"login_token:{login_token}", expires=True)
    if not sid:
        frappe.respond_as_web_page(_("Invalid Request"), _("Invalid Login Token"), http_status_code=417); return
    frappe.local.form_dict.sid = sid
    frappe.local.login_manager = LoginManager()
    redirect_post_login(desk_user=frappe.db.get_value("User", frappe.session.user, "user_type") == "System User")

def get_login_with_email_link_ratelimit() -> int:
    return frappe.get_system_settings("rate_limit_email_link_login") or 5

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=get_login_with_email_link_ratelimit, seconds=60*60)
def send_login_link(email: str):
    if not frappe.get_system_settings("login_with_email_link"): return
    expiry = frappe.get_system_settings("login_with_email_link_expiry") or 10
    link = _generate_temporary_login_link(email, expiry)
    app_name = (frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or _("Framework"))
    subject = _("Login To {0}").format(app_name)
    frappe.sendmail(subject=subject, recipients=email, template="login_with_email_link",
        args={"link":link,"minutes":expiry,"app_name":app_name}, now=True)

def _generate_temporary_login_link(email: str, expiry: int):
    assert isinstance(email, str)
    if not frappe.db.exists("User", email):
        frappe.throw(_("User with email address {0} does not exist").format(email), frappe.DoesNotExistError)
    key = frappe.generate_hash()
    frappe.cache.set_value(f"one_time_login_key:{key}", email, expires_in_sec=expiry*60)
    return get_url(f"/api/method/frappe.www.login.login_via_key?key={key}")

@frappe.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=get_login_with_email_link_ratelimit, seconds=60*60)
def login_via_key(key: str):
    cache_key = f"one_time_login_key:{key}"
    email = frappe.cache.get_value(cache_key)
    if email:
        frappe.cache.delete_value(cache_key)
        frappe.local.login_manager.login_as(email)
        redirect_post_login(desk_user=frappe.db.get_value("User", frappe.session.user, "user_type") == "System User")
    else:
        frappe.respond_as_web_page(_("Not Permitted"),
            _("The link you trying to login is invalid or expired."),
            http_status_code=403, indicator_color="red")

def sanitize_redirect(redirect):
    if not redirect: return redirect
    parsed_redirect = urlparse(redirect)
    if not parsed_redirect.netloc: return redirect
    parsed_request_host = urlparse(frappe.local.request.url)
    if parsed_request_host.netloc == parsed_redirect.netloc: return redirect
    return None
