"""
Portal Theme patcher.

  apply_01_v2 / rollback_01_v2  -> desk baseline
  apply_02    / rollback_02     -> login brand match
  apply_05_fixes                -> Patch 05: compact login, sidebar gap fix,
                                  status pill visibility, light-yellow field bg,
                                  reset old hardcoded strings
  rollback_05_fixes             -> revert Patch 05 additions
"""
import os, re, datetime, shutil, frappe

BENCH_DIR       = os.path.expanduser("~/frappe-bench")
APP_ROOT        = os.path.join(BENCH_DIR, "apps/portal_theme/portal_theme")
APP_WWW_DIR     = os.path.join(APP_ROOT, "www")
APP_JS_DIR      = os.path.join(APP_ROOT, "public/js")
LOGIN_HTML_PATH = os.path.join(APP_WWW_DIR, "login.html")
LOGIN_PY_PATH   = os.path.join(APP_WWW_DIR, "login.py")
PORTAL_JS_PATH  = os.path.join(APP_JS_DIR,  "portal_theme.js")

TEMPLATE      = "16.0.0-dev"
BACKUP_DIR    = os.path.expanduser("~/pt_theme_backups")
PRISTINE_FILE = os.path.join(BACKUP_DIR, "_PRISTINE_theme_template.css")

os.makedirs(BACKUP_DIR, exist_ok=True)


def _ts(): return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def _timestamp_backup_css(tag):
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    path = os.path.join(BACKUP_DIR, f"theme_template_{_ts()}_{tag}.css")
    with open(path, "w") as f: f.write(current)
    print(f"[backup:css] {path}")

def _ensure_pristine_css():
    if os.path.exists(PRISTINE_FILE): return
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    cleaned = re.sub(r"/\* PT-PATCH:[\w\-]+ BEGIN \*/.*?/\* PT-PATCH:[\w\-]+ END \*/",
                     "", current, flags=re.DOTALL).rstrip() + "\n"
    with open(PRISTINE_FILE, "w") as f: f.write(cleaned)
    print(f"[pristine] {PRISTINE_FILE}")

def _save_css(new_css):
    frappe.db.set_value("Theme Template", TEMPLATE, "theme_template", new_css)
    active = frappe.db.get_value("Portal Theme", {"is_active": 1}, "name")
    if active:
        frappe.get_doc("Portal Theme", active).save(ignore_permissions=True)
        print(f"[portal-theme] re-saved '{active}'")
    frappe.db.commit(); frappe.clear_cache()

def _ensure_active_theme():
    if frappe.db.get_value("Portal Theme", {"is_active": 1}, "name"): return
    if not frappe.db.exists("Portal Theme", "Dalmar Brand"):
        d = frappe.new_doc("Portal Theme")
        d.theme_name="Dalmar Brand"; d.is_active=1
        d.primary="#3ECF57"; d.secondary="#17304D"; d.accent="#2A5A80"; d.neutral="#EEF2F7"
        d.border_color="#E1E7EE"; d.border_radius=8; d.theme_template=TEMPLATE
        d.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Portal Theme", "Dalmar Brand", "is_active", 1)
        frappe.get_doc("Portal Theme", "Dalmar Brand").save(ignore_permissions=True)

def _ensure_original_file(src_path, tag):
    fixed = os.path.join(BACKUP_DIR, f"_ORIGINAL_{tag}")
    if os.path.exists(fixed) or not os.path.exists(src_path): return
    shutil.copy2(src_path, fixed); print(f"[original] {fixed}")

def _timestamp_backup_file(src_path, tag):
    if not os.path.exists(src_path): return
    dst = os.path.join(BACKUP_DIR, f"{tag}_{_ts()}")
    shutil.copy2(src_path, dst); print(f"[backup:file] {dst}")


# =====================================================
# BASELINE CSS — Patch 05: sidebar gap fix, pills, field bg
# =====================================================
BASELINE_CSS = r"""
:root {
    --pt-green: #3ECF57; --pt-green-2: #2FB84A;
    --pt-navy:  #17304D; --pt-navy-2:  #0F2338; --pt-navy-light: #2A5A80;
    --pt-bg: #F4F6FA; --pt-surface: #FFFFFF; --pt-surface-alt: #F7F9FC; --pt-surface-2: #EEF2F7;
    --pt-border: #E1E7EE; --pt-border-strong: #C7D0DB;
    --pt-text: #1B2431; --pt-text-2: #2E3B4E; --pt-text-muted: #5A6B80; --pt-text-inverse: #FFFFFF;
    --pt-field-bg: #FFFDF3;   /* Very light warm yellow — ONLY inside form controls */
    --pt-radius-sm: 4px; --pt-radius-md: 8px; --pt-radius-lg: 12px;
    --pt-shadow-sm: 0 1px 2px rgba(23,48,77,0.06);
    --pt-shadow-md: 0 4px 14px rgba(23,48,77,0.10);
    --pt-shadow-lg: 0 10px 30px rgba(23,48,77,0.14);
    --pt-focus-ring: 0 0 0 3px rgba(62,207,87,0.35);
    --primary:#3ECF57; --secondary:#17304D; --accent:#2A5A80; --neutral:#EEF2F7;
    --primary-text-color:#FFFFFF; --secondary-text-color:#FFFFFF;
    --primary-text-color-light:#FFFFFF; --secondary-text-color-light:#FFFFFF;
}
:root[data-theme="dark"] {
    --pt-bg: #0D1929; --pt-surface: #1A2436; --pt-surface-alt: #142032; --pt-surface-2: #1E2A3E;
    --pt-border: #2A3548; --pt-border-strong: #3A4558;
    --pt-text: #E6EAF0; --pt-text-2: #C8CFD8; --pt-text-muted: #8A96A5;
    --pt-field-bg: #1E2A3E;
    --pt-shadow-sm: 0 1px 2px rgba(0,0,0,0.30);
    --pt-shadow-md: 0 4px 14px rgba(0,0,0,0.35);
    --pt-shadow-lg: 0 10px 30px rgba(0,0,0,0.45);
}

body, .desk-page, .layout-main, .layout-main-section, .page-container, .page-body, .main-section {
    background: var(--pt-bg) !important; color: var(--pt-text) !important;
}

/* ============ TOP STRIP — diagonal ============ */
.page-head, .page-head-content, .navbar, .desk-topbar, header.navbar-header {
    background: linear-gradient(105deg,
        var(--pt-green) 0%, var(--pt-green) 38%,
        var(--pt-navy)  42%, var(--pt-navy) 100%) !important;
    border-bottom: 0 !important;
    box-shadow: var(--pt-shadow-md) !important;
    min-height: 52px !important;
}
/* Surgical white text — exempt indicator pills, dropdowns, buttons */
.page-head .title-area,
.page-head .title-area h1, .page-head .title-area h2, .page-head .title-area h3,
.page-head .title-area h4, .page-head .title-area .title-text,
.page-head .breadcrumb-container, .page-head .breadcrumb-container a,
.page-head .breadcrumb, .page-head .breadcrumb a, .page-head .breadcrumb-item,
.page-head .page-title,
.page-head .sidebar-toggle-btn, .page-head .toggle-sidebar,
.navbar .navbar-brand, .navbar-home {
    color: var(--pt-text-inverse) !important;
}
.page-head .breadcrumb a, .page-head .breadcrumb-container a { opacity: 0.9; }
.page-head .breadcrumb a:hover, .page-head .breadcrumb-container a:hover { opacity: 1; }

/* ============ INDICATOR PILLS in page-head — visible with proper colors ============ */
.page-head .indicator-pill, .page-head .indicator,
.page-head .title-area .indicator-pill, .page-head .title-area .indicator,
.page-head .badge {
    color: initial !important;
    background: none;
    border-radius: 999px !important;
    padding: 2px 10px !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    line-height: 1.6 !important;
    display: inline-block;
}
.page-head .indicator-pill.gray, .page-head .indicator.gray,
.page-head .indicator-pill.grey, .page-head .indicator.grey {
    background: rgba(255,255,255,0.92) !important; color: #17304D !important;
}
.page-head .indicator-pill.orange, .page-head .indicator.orange {
    background: #F97316 !important; color: #FFFFFF !important;
}
.page-head .indicator-pill.yellow, .page-head .indicator.yellow {
    background: #FCD34D !important; color: #17304D !important;
}
.page-head .indicator-pill.green, .page-head .indicator.green {
    background: #10B981 !important; color: #FFFFFF !important;
}
.page-head .indicator-pill.red, .page-head .indicator.red {
    background: #EF4444 !important; color: #FFFFFF !important;
}
.page-head .indicator-pill.blue, .page-head .indicator.blue {
    background: #3B82F6 !important; color: #FFFFFF !important;
}
.page-head .indicator-pill.lightblue { background: #93C5FD !important; color: #17304D !important; }
.page-head .indicator-pill.purple { background: #8B5CF6 !important; color: #FFFFFF !important; }
.page-head .indicator-pill.pink { background: #EC4899 !important; color: #FFFFFF !important; }
.page-head .indicator-pill.darkgrey, .page-head .indicator-pill.darkgray {
    background: #6B7280 !important; color: #FFFFFF !important;
}

/* ============ PAGE HEAD BUTTONS ============ */
.page-head .custom-actions .btn,
.page-head .standard-actions .btn:not(.btn-primary),
.page-head .page-actions .btn:not(.btn-primary),
.page-head .menu-btn-group .btn,
.page-head .btn.btn-default,
.page-head .btn-secondary,
.page-head .dropdown-toggle {
    background: rgba(255,255,255,0.95) !important;
    color: var(--pt-navy) !important;
    border: 0 !important;
    border-radius: 999px !important;
    font-weight: 500 !important;
    padding: 4px 14px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
}
.page-head .custom-actions .btn:hover,
.page-head .btn.btn-default:hover,
.page-head .dropdown-toggle:hover {
    background: #FFFFFF !important;
}
.page-head .primary-action,
.page-head .btn.btn-primary,
.page-head .standard-actions .btn-primary {
    background: var(--pt-green) !important; color: var(--pt-navy) !important;
    border: 0 !important; border-radius: 999px !important;
    font-weight: 700 !important; padding: 5px 16px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}
.page-head .primary-action:hover, .page-head .btn.btn-primary:hover {
    background: var(--pt-green-2) !important; color: var(--pt-navy) !important;
}
.page-head .btn.btn-actions, .page-head .btn-actions-menu {
    background: rgba(255,255,255,0.95) !important;
    color: var(--pt-navy) !important;
    border-radius: 999px !important;
}

/* ============ DROPDOWN MENUS ============ */
.page-head .dropdown-menu, .navbar .dropdown-menu,
.custom-actions .dropdown-menu, .page-actions .dropdown-menu,
.standard-actions .dropdown-menu, .menu-btn-group .dropdown-menu {
    background-color: var(--pt-surface) !important;
    border: 1px solid var(--pt-border) !important;
    box-shadow: var(--pt-shadow-lg) !important;
    border-radius: var(--pt-radius-md) !important;
    padding: 6px 0 !important;
}
.page-head .dropdown-menu *, .navbar .dropdown-menu * { color: var(--pt-text) !important; }
.page-head .dropdown-menu .dropdown-item, .page-head .dropdown-menu a,
.navbar .dropdown-menu .dropdown-item, .navbar .dropdown-menu a {
    color: var(--pt-text) !important; padding: 8px 16px !important; background: transparent !important;
}
.page-head .dropdown-menu .dropdown-item:hover,
.page-head .dropdown-menu a:hover,
.navbar .dropdown-menu .dropdown-item:hover {
    background: var(--pt-surface-2) !important; color: var(--pt-navy) !important;
}
:root[data-theme="dark"] .page-head .dropdown-menu .dropdown-item:hover {
    background: var(--pt-surface-alt) !important; color: var(--pt-green) !important;
}

/* ============ LEFT SIDEBAR — no gap, solid selected ============ */
.body-sidebar, .body-sidebar-container, .desk-sidebar, .layout-side-section {
    background: var(--pt-navy) !important;
    color: rgba(255,255,255,0.88) !important;
    border-right: 0 !important;
}

/* Kill all list default spacing */
.body-sidebar ul, .body-sidebar ol,
.desk-sidebar ul, .desk-sidebar ol,
.body-sidebar-container ul, .body-sidebar-container ol,
.layout-side-section ul, .layout-side-section ol {
    margin: 0 !important; padding: 0 !important; list-style: none !important;
}
.body-sidebar li, .desk-sidebar li,
.body-sidebar-container li, .layout-side-section li {
    margin: 0 !important; padding: 0 !important; list-style: none !important;
}

/* Item styling — ONLY on the clickable element */
.body-sidebar .sidebar-item,
.body-sidebar .standard-sidebar-item,
.body-sidebar .desk-sidebar-item,
.desk-sidebar .sidebar-item,
.desk-sidebar .standard-sidebar-item,
.desk-sidebar-item.standard-sidebar-item,
.layout-side-section .sidebar-item {
    color: rgba(255,255,255,0.88) !important;
    background: transparent !important;
    border-radius: 4px !important;
    padding: 6px 12px !important;
    margin: 0 !important;
    text-decoration: none !important;
    transition: background 0.12s ease, color 0.12s ease;
    display: flex; align-items: center;
    line-height: 1.4 !important;
}
.body-sidebar .sidebar-item *,
.desk-sidebar-item.standard-sidebar-item * {
    color: inherit !important; background: transparent !important;
}

/* Hover — soft glass */
.body-sidebar .sidebar-item:hover,
.body-sidebar .standard-sidebar-item:hover,
.desk-sidebar .sidebar-item:hover,
.desk-sidebar-item.standard-sidebar-item:hover {
    background: rgba(255,255,255,0.10) !important;
    color: #FFFFFF !important;
}
.body-sidebar .sidebar-item:hover *,
.desk-sidebar-item.standard-sidebar-item:hover * { color: #FFFFFF !important; }

/* Selected — solid green, navy text */
.body-sidebar .sidebar-item.selected,
.body-sidebar .standard-sidebar-item.selected,
.body-sidebar .desk-sidebar-item.selected,
.body-sidebar .sidebar-item.active,
.desk-sidebar .sidebar-item.selected,
.desk-sidebar .standard-sidebar-item.selected,
.desk-sidebar-item.standard-sidebar-item.selected,
.desk-sidebar-item.selected,
.body-sidebar [aria-current="page"] {
    background: var(--pt-green) !important;
    color: var(--pt-navy) !important;
    font-weight: 700 !important;
}
.body-sidebar .sidebar-item.selected *,
.desk-sidebar-item.standard-sidebar-item.selected *,
.desk-sidebar-item.selected * {
    color: var(--pt-navy) !important; background: transparent !important;
}

.body-sidebar .standard-sidebar-section .sidebar-section-title,
.desk-sidebar .standard-sidebar-section-title {
    color: rgba(255,255,255,0.5) !important;
    font-size: 11px !important; text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 8px 12px 4px !important;
}

/* ============ WORKSPACE / WIDGETS (kept white, no yellow) ============ */
.workspace-body { background: var(--pt-bg) !important; padding-top: 16px; }
.widget, .shortcut-widget-box, .widget.card-box {
    background: var(--pt-surface) !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: var(--pt-radius-md) !important;
    box-shadow: var(--pt-shadow-sm) !important;
    color: var(--pt-text) !important;
    transition: 0.2s ease all;
}
.widget:hover { box-shadow: var(--pt-shadow-md) !important; transform: translateY(-2px); }
.widget .widget-head, .widget .widget-title .ellipsis {
    color: var(--pt-navy) !important; font-weight: 600 !important;
}
:root[data-theme="dark"] .widget .widget-head,
:root[data-theme="dark"] .widget .widget-title .ellipsis { color: var(--pt-green) !important; }

/* ============ BUTTONS (outside page-head) ============ */
.btn.btn-primary {
    background: var(--pt-navy) !important; color: var(--pt-text-inverse) !important;
    border: 0 !important; border-radius: var(--pt-radius-md) !important; font-weight: 600 !important;
}
.btn.btn-primary:hover { background: var(--pt-navy-2) !important; }
.btn.btn-secondary, .btn.btn-default {
    background: var(--pt-surface) !important; color: var(--pt-text) !important;
    border: 1px solid var(--pt-border-strong) !important; border-radius: var(--pt-radius-md) !important;
}

/* ============ FORM FIELDS — LIGHT YELLOW INSIDE ONLY ============ */
.form-control:not([type="checkbox"]):not([type="radio"]),
.input-with-feedback,
.like-disabled-input,
input[type="text"].form-control,
input[type="email"].form-control,
input[type="password"].form-control,
input[type="number"].form-control,
input[type="date"].form-control,
input[type="datetime-local"].form-control,
input[type="time"].form-control,
input[type="search"].form-control,
input[type="tel"].form-control,
input[type="url"].form-control,
select.form-control,
textarea.form-control,
.awesomplete input.form-control,
.frappe-control input.form-control {
    background: var(--pt-field-bg) !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: var(--pt-radius-md) !important;
    color: var(--pt-text) !important;
    box-shadow: none !important;
}
.form-control:focus, .input-with-feedback:focus {
    border-color: var(--pt-green) !important;
    box-shadow: var(--pt-focus-ring) !important;
    outline: 0 !important;
    background: var(--pt-field-bg) !important;
}
/* Read-only + disabled — slightly muted so users see them */
.form-control[readonly], .form-control:disabled,
.like-disabled-input {
    background: var(--pt-surface-2) !important;
    color: var(--pt-text-muted) !important;
}

.control-label, .grid-heading-row { color: var(--pt-text-2) !important; font-weight: 600 !important; }
.form-section .section-head, .section-head { color: var(--pt-navy) !important; }
:root[data-theme="dark"] .form-section .section-head,
:root[data-theme="dark"] .section-head { color: var(--pt-green) !important; }
h1, h2, h3, h4, h5, h6 { color: var(--pt-text) !important; }

/* Login page must NOT get the yellow (it has its own compact style) */
.for-login .form-control, .for-forgot .form-control,
.for-email-login .form-control, .for-login-with-email-link .form-control,
.for-signup .form-control {
    background: transparent !important;
}
"""


def apply_01_v2():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _ensure_pristine_css(); _timestamp_backup_css("before_baseline")
    _ensure_active_theme(); _save_css(BASELINE_CSS.strip() + "\n")
    print("[done] Baseline CSS installed.")


def rollback_01_v2():
    if not os.path.exists(PRISTINE_FILE):
        print(">>> No pristine CSS backup."); return
    _timestamp_backup_css("before_ROLLBACK_baseline")
    with open(PRISTINE_FILE) as f: _save_css(f.read())
    if frappe.db.exists("Portal Theme", "Dalmar Brand"):
        frappe.db.set_value("Portal Theme", "Dalmar Brand", "is_active", 0)
    print("[done] Baseline rolled back.")


# =====================================================
# CUSTOM FIELDS (same as before)
# =====================================================
CUSTOM_FIELDS_02 = [
    {"fieldname":"brand_login_section","label":"Brand Login Design","fieldtype":"Section Break","insert_after":"completely_hide_footer_from_login_page"},
    {"fieldname":"login_navbar_use_diagonal","label":"Use Diagonal Navbar","fieldtype":"Check","default":"1","insert_after":"brand_login_section"},
    {"fieldname":"login_navbar_color_2","label":"Navbar Second Color","fieldtype":"Color","insert_after":"login_navbar_use_diagonal"},
    {"fieldname":"login_navbar_right_text","label":"Navbar Right Text","fieldtype":"Data","default":"Login","insert_after":"login_navbar_color_2"},
    {"fieldname":"col_break_bl_1","fieldtype":"Column Break","insert_after":"login_navbar_right_text"},
    {"fieldname":"login_footer_color","label":"Footer Color 1","fieldtype":"Color","insert_after":"col_break_bl_1"},
    {"fieldname":"login_footer_color_2","label":"Footer Color 2","fieldtype":"Color","insert_after":"login_footer_color"},
    {"fieldname":"login_footer_text_color","label":"Footer Text Color","fieldtype":"Color","insert_after":"login_footer_color_2"},
    {"fieldname":"login_card_section","label":"Login Card","fieldtype":"Section Break","insert_after":"login_footer_text_color"},
    {"fieldname":"login_card_background","label":"Card Background","fieldtype":"Color","insert_after":"login_card_section"},
    {"fieldname":"login_card_border_radius","label":"Card Border Radius (px)","fieldtype":"Int","default":"15","insert_after":"login_card_background"},
    {"fieldname":"col_break_bl_2","fieldtype":"Column Break","insert_after":"login_card_border_radius"},
    {"fieldname":"login_card_max_width","label":"Card Max Width (px)","fieldtype":"Int","default":"400","insert_after":"col_break_bl_2"},
    {"fieldname":"login_subtitle","label":"Card Subtitle (empty = default Company)","fieldtype":"Data","insert_after":"login_card_max_width"},
    {"fieldname":"login_btn_section","label":"Login Button","fieldtype":"Section Break","insert_after":"login_subtitle"},
    {"fieldname":"login_button_use_diagonal","label":"Use Diagonal Button","fieldtype":"Check","default":"1","insert_after":"login_btn_section"},
    {"fieldname":"login_button_bg_1","label":"Button Color 1","fieldtype":"Color","insert_after":"login_button_use_diagonal"},
    {"fieldname":"login_button_bg_2","label":"Button Color 2","fieldtype":"Color","insert_after":"login_button_bg_1"},
    {"fieldname":"col_break_bl_3","fieldtype":"Column Break","insert_after":"login_button_bg_2"},
    {"fieldname":"login_button_text","label":"Button Text Color","fieldtype":"Color","insert_after":"col_break_bl_3"},
    {"fieldname":"login_content_section","label":"Card Footer Content (empty = auto)","fieldtype":"Section Break","insert_after":"login_button_text"},
    {"fieldname":"login_terms_text","label":"Terms Text (HTML) — empty = Website Settings copyright","fieldtype":"Text Editor","insert_after":"login_content_section"},
    {"fieldname":"col_break_bl_4","fieldtype":"Column Break","insert_after":"login_terms_text"},
    {"fieldname":"login_copyright_text","label":"Footer Bar Text — empty = auto","fieldtype":"Data","insert_after":"col_break_bl_4"},
    {"fieldname":"login_powered_by_text","label":"Powered By Text — empty = Website Settings footer_powered","fieldtype":"Data","insert_after":"login_copyright_text"},
    {"fieldname":"login_powered_by_url","label":"Powered By URL","fieldtype":"Data","insert_after":"login_powered_by_text"},
    {"fieldname":"login_social_section","label":"Social Links","fieldtype":"Section Break","insert_after":"login_powered_by_url"},
    {"fieldname":"login_show_social_icons","label":"Show Social Icons","fieldtype":"Check","default":"1","insert_after":"login_social_section"},
    {"fieldname":"login_facebook_url","label":"Facebook URL","fieldtype":"Data","insert_after":"login_show_social_icons"},
    {"fieldname":"login_twitter_url","label":"Twitter/X URL","fieldtype":"Data","insert_after":"login_facebook_url"},
    {"fieldname":"col_break_bl_5","fieldtype":"Column Break","insert_after":"login_twitter_url"},
    {"fieldname":"login_linkedin_url","label":"LinkedIn URL","fieldtype":"Data","insert_after":"col_break_bl_5"},
    {"fieldname":"login_instagram_url","label":"Instagram URL","fieldtype":"Data","insert_after":"login_linkedin_url"},
]

def _add_custom_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_field
    added = 0
    for fld in CUSTOM_FIELDS_02:
        cf = f"Portal Theme Setting-{fld['fieldname']}"
        if frappe.db.exists("Custom Field", cf): continue
        create_custom_field("Portal Theme Setting", fld); added += 1
    frappe.clear_cache(doctype="Portal Theme Setting")
    print(f"[custom-fields] added {added}")

def _remove_custom_fields():
    for fld in CUSTOM_FIELDS_02:
        cf = f"Portal Theme Setting-{fld['fieldname']}"
        if frappe.db.exists("Custom Field", cf):
            frappe.delete_doc("Custom Field", cf, force=1, ignore_permissions=True)
    frappe.clear_cache(doctype="Portal Theme Setting")

def _set_login_visual_defaults():
    """ONLY visual defaults (colors, sizes). NEVER text content."""
    doc = frappe.get_single("Portal Theme Setting")
    defaults = {
        "apply_on_login_page":1, "login_navbar_use_diagonal":1,
        "login_navbar":"#3ECF57", "login_navbar_color_2":"#17304D", "login_navbar_text":"#FFFFFF",
        "login_navbar_right_text":"Login",
        "login_footer_color":"#3ECF57", "login_footer_color_2":"#17304D", "login_footer_text_color":"#FFFFFF",
        "login_card_background":"#F7F0E7", "login_card_border_radius":15, "login_card_max_width":400,
        "login_button_use_diagonal":1, "login_button_bg_1":"#3ECF57", "login_button_bg_2":"#17304D",
        "login_button_text":"#FFFFFF",
    }
    for k, v in defaults.items():
        cur = doc.get(k)
        empty = cur in (None, "") or (isinstance(cur, int) and cur == 0
                and k not in ("login_card_border_radius","login_card_max_width"))
        if empty: doc.set(k, v)
    doc.save(ignore_permissions=True)

# --- Clear the old Patch-02 hardcoded text (only if user hasn't changed it) ---
_OLD_HARDCODED_STRINGS = {
    "login_copyright_text": "© 2024 Baarjeex Group of Companies.",
    "login_terms_text": "© 2024 Baarjeex, Inc. All rights reserved. Baarjeex, Technology, Terms and conditions, subject to change without notice.",
    "login_powered_by_text": "Powered by DagaarTech®",
    "login_powered_by_url": "https://dagaartech.com",
}
def _reset_old_hardcoded():
    doc = frappe.get_single("Portal Theme Setting")
    changed = False
    for k, old in _OLD_HARDCODED_STRINGS.items():
        try:
            cur = doc.get(k)
            if cur and str(cur).strip() == old:
                doc.set(k, "")
                changed = True
                print(f"[reset] cleared '{k}' (was old hardcoded default)")
        except Exception:
            pass
    if changed:
        doc.save(ignore_permissions=True)


# =====================================================
# LOGIN HTML — v14-compact aesthetic, brand navbar+footer,
#              ALL text from settings
# =====================================================
LOGIN_HTML = r"""{% extends "templates/web.html" %}
{# Portal Theme login — Patch 05, based on user's v14 file, brand-integrated #}

{% macro social_icon(name) -%}
{% if name == 'facebook' %}<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.51 1.49-3.9 3.78-3.9 1.09 0 2.24.2 2.24.2v2.46H15.2c-1.24 0-1.63.77-1.63 1.56V12h2.77l-.44 2.89h-2.33v6.99A10 10 0 0 0 22 12z"/></svg>{% endif %}
{% if name == 'twitter' %}<svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25h6.83l4.713 6.231 5.447-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z"/></svg>{% endif %}
{% if name == 'linkedin' %}<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14Zm-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79ZM6.88 8.56A1.68 1.68 0 0 0 8.56 6.88 1.69 1.69 0 0 0 6.88 5.19 1.69 1.69 0 0 0 5.19 6.88c0 .93.76 1.68 1.69 1.68ZM8.27 18.5v-8.37H5.5v8.37h2.77Z"/></svg>{% endif %}
{% if name == 'instagram' %}<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M7.8 2h8.4A5.8 5.8 0 0 1 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8A5.8 5.8 0 0 1 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2Zm-.2 2A3.6 3.6 0 0 0 4 7.6v8.8A3.6 3.6 0 0 0 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6A3.6 3.6 0 0 0 16.4 4H7.6Zm9.65 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/></svg>{% endif %}
{%- endmacro %}

{% macro email_login_body() -%}
{% if not disable_user_pass_login or (ldap_settings and ldap_settings.enabled) %}
<div class="page-card-body">
    <div class="form-group">
        <label class="form-label sr-only" for="login_email">{{ login_label or _("Email")}}</label>
        <div class="email-field">
            <input type="text" id="login_email" class="form-control"
                placeholder="{% if login_name_placeholder %}{{ login_name_placeholder }}{% else %}{{ _('jane@example.com') }}{% endif %}"
                required autofocus autocomplete="username">
            <svg class="field-icon email-icon" width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.5 7.65V15c0 .36.14.7.4.96.26.26.6.4.96.4h12.28c.36 0 .7-.14.96-.4.26-.26.4-.6.4-.96V7.65" stroke="#8A96A5" stroke-width="1.3" stroke-linecap="round"/>
                <path d="M17.5 7.58V5.53c0-.36-.14-.7-.4-.96-.26-.26-.6-.4-.96-.4H3.86c-.36 0-.7.14-.96.4-.26.26-.4.6-.4.96v2.05L10 10.83l7.5-3.25Z" stroke="#8A96A5" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
        </div>
    </div>
    <div class="form-group">
        <label class="form-label sr-only" for="login_password">{{ _("Password") }}</label>
        <div class="password-field">
            <input type="password" id="login_password" class="form-control" placeholder="•••••" autocomplete="current-password" required>
            <svg class="field-icon password-icon" width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4.3 6.5h11.4c1.1 0 2 .9 2 2v7.5c0 1.1-.9 2-2 2H4.3c-1.1 0-2-.9-2-2V8.5c0-1.1.9-2 2-2Z" stroke="#8A96A5" stroke-width="1.3"/>
                <path d="M6 6.5V6c0-2.2 1.8-4 4-4s4 1.8 4 4v.5" stroke="#8A96A5" stroke-width="1.3" stroke-linecap="round"/>
                <circle cx="10" cy="12" r="1.3" fill="#8A96A5"/>
            </svg>
            <span toggle="#login_password" class="toggle-password text-muted">{{ _('Show') }}</span>
        </div>
    </div>
    {% if not disable_user_pass_login %}
    <p class="forgot-password-message"><a href="#forgot">{{ _("Forgot Password?") }}</a></p>
    {% endif %}
</div>
{% endif %}
<div class="page-card-actions">
    {% if not disable_user_pass_login %}
    <button class="btn btn-sm btn-primary btn-block btn-login" type="submit">{{ _("Login") }}</button>
    {% endif %}
    {% if ldap_settings and ldap_settings.enabled %}
    <button class="btn btn-sm btn-default btn-block btn-login btn-ldap-login">{{ _("Login with LDAP") }}</button>
    {% endif %}
</div>
{%- endmacro %}

{% macro brand_card_extras() %}
<div class="brand-login-extras">
    {% if brand_login.terms_text %}
    <div class="brand-login-terms">{{ brand_login.terms_text | safe }}</div>
    {% endif %}
    {% if brand_login.powered_by_text %}
    <div class="brand-login-powered">
        <a href="{{ brand_login.powered_by_url or '#' }}" target="_blank" rel="noopener">{{ brand_login.powered_by_text }}</a>
    </div>
    {% endif %}
    {% if brand_login.show_social_icons and (brand_login.social.facebook or brand_login.social.twitter or brand_login.social.linkedin or brand_login.social.instagram) %}
    <div class="brand-login-social">
        {% if brand_login.social.facebook %}<a href="{{ brand_login.social.facebook }}" target="_blank" rel="noopener" aria-label="Facebook">{{ social_icon('facebook') }}</a>{% endif %}
        {% if brand_login.social.twitter %}<a href="{{ brand_login.social.twitter }}" target="_blank" rel="noopener" aria-label="Twitter">{{ social_icon('twitter') }}</a>{% endif %}
        {% if brand_login.social.linkedin %}<a href="{{ brand_login.social.linkedin }}" target="_blank" rel="noopener" aria-label="LinkedIn">{{ social_icon('linkedin') }}</a>{% endif %}
        {% if brand_login.social.instagram %}<a href="{{ brand_login.social.instagram }}" target="_blank" rel="noopener" aria-label="Instagram">{{ social_icon('instagram') }}</a>{% endif %}
    </div>
    {% endif %}
</div>
{% endmacro %}

{% macro logo_section(title=null) %}
<div class="page-card-head">
    <img class="app-logo" src="{{ logo }}" alt="logo">
    {% if title %}
        <h4 class="brand-heading">{{ _(title) }}</h4>
    {% else %}
        <h4 class="brand-heading">{{ _('Login to {0}').format(app_name or _("Framework")) }}</h4>
        {% if brand_login.subtitle %}
        <div class="brand-subtitle">{{ brand_login.subtitle }}</div>
        {% endif %}
    {% endif %}
</div>
{% endmacro %}

{% block head_include %}
<title>{{ app_name or "Login" }}</title>
<meta property="og:title" content="{{ app_name or 'Login' }}">
{% if brand_login.og_description %}<meta property="og:description" content="{{ brand_login.og_description }}">{% endif %}
<meta property="og:image" content="{{ logo }}">
{{ include_style('login.bundle.css') }}
{% set bl = brand_login %}
<style>
:root {
    --bl-nav-1:{{ bl.nav_bg1 }};  --bl-nav-2:{{ bl.nav_bg2 }};   --bl-nav-text:{{ bl.nav_text }};
    --bl-foot-1:{{ bl.footer_bg1 }}; --bl-foot-2:{{ bl.footer_bg2 }}; --bl-foot-text:{{ bl.footer_text }};
    --bl-card-bg:{{ bl.card_bg }};
    --bl-card-radius:{{ bl.card_radius }}px;
    --bl-card-max:{{ bl.card_max_width }}px;
    --bl-card-op:{{ bl.card_opacity }};
    --bl-btn-1:{{ bl.btn_bg1 }};  --bl-btn-2:{{ bl.btn_bg2 }};   --bl-btn-text:{{ bl.btn_text }};
    --bl-underline:#C5A880;
    --bl-underline-focus:{{ bl.btn_bg1 }};
    --bl-input-text:#3A3428;
    --bl-terms-text:#6B6455;
    --bl-subtitle:#3A4658;
    --bl-page-bg:#F5F5F0;
}
html, body { background: var(--bl-page-bg) !important; min-height:100vh; }
body {
    display:flex; flex-direction:column;
    {% if apply_image_or_color == "Image" and background_image %}
        background: url('{{ background_image }}') no-repeat center center fixed !important; background-size: cover !important;
    {% elif apply_image_or_color == "Color" and background_color %}
        background: {{ background_color }} !important;
    {% elif apply_image_or_color == "Slider" and background_slider_images %}
        background: url('{{ background_slider_images[0] }}') no-repeat center center fixed !important; background-size: cover !important;
    {% endif %}
}
{% if (apply_image_or_color == "Image" and background_image) or apply_image_or_color == "Slider" %}
body::before { content:""; position:fixed; inset:0; background:rgba(0,0,0,{{ background_opacity or 0.2 }}); z-index:0; }
body > * { position: relative; z-index: 1; }
{% endif %}
.web-body-wrapper { min-height:100vh; display:flex; flex-direction:column; }
.web-page-content, .page-content, .container { flex: 1 0 auto; }

/* ==== NAVBAR (brand diagonal) ==== */
.navbar, header .navbar {
    {% if bl.nav_use_diagonal %}
    background: linear-gradient(105deg,
        var(--bl-nav-1) 0%, var(--bl-nav-1) 55%,
        var(--bl-nav-2) 60%, var(--bl-nav-2) 100%) !important;
    {% else %}
    background: var(--bl-nav-1) !important;
    {% endif %}
    border-bottom:0 !important; box-shadow:0 4px 14px rgba(23,48,77,0.10) !important;
    min-height:64px !important; padding:0 26px !important; position:relative;
}
.navbar-brand, .navbar .navbar-brand { color: var(--bl-nav-text) !important; padding: 8px 0 !important; }
.navbar-brand img, .navbar .app-logo { max-height: 40px !important; width: auto !important; }
.navbar::after {
    content: "{{ bl.nav_right_text }}";
    position: absolute; right: 36px; top: 50%; transform: translateY(-50%);
    color: var(--bl-nav-text); font-weight: 600; font-size: 17px; letter-spacing: 0.02em;
    pointer-events: none;
}
.navbar .navbar-nav, .navbar .navbar-collapse .navbar-nav { display: none !important; }

/* ==== LOGIN CARD — compact v14 style ==== */
.for-login .page-card, .for-forgot .page-card, .for-login-with-email-link .page-card,
.for-signup .page-card, .for-email-login .page-card {
    background: var(--bl-card-bg) !important;
    border-radius: var(--bl-card-radius) !important;
    border: 0 !important;
    max-width: var(--bl-card-max) !important;
    width: 90% !important;
    padding: 26px 26px 20px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.10) !important;
    opacity: var(--bl-card-op);
    text-align: center;
    {% if position_of_login_card == 1 %}margin: 40px auto 40px 5vw !important;
    {% elif position_of_login_card == 2 %}margin: 40px 5vw 40px auto !important;
    {% else %}margin: 40px auto !important;{% endif %}
}
.for-login section, .for-forgot section, .for-email-login section,
.for-signup section, .for-login-with-email-link section { padding: 0 !important; }

/* Header */
.page-card-head { padding: 0 0 18px !important; text-align: center !important; border-bottom: 0 !important; }
.page-card-head img.app-logo {
    display: block; margin: 0 auto 8px;
    max-height: 44px; width: auto;
}
.page-card-head .brand-heading {
    color: var(--bl-nav-2) !important;
    font-size: 15px !important; font-weight: 700 !important;
    margin: 0 0 3px !important; letter-spacing: 0.01em;
}
.page-card-head .brand-subtitle {
    color: var(--bl-subtitle);
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin: 2px 0 0;
}

/* Inputs — border-bottom underline (v14 style) */
.for-login .form-control, .for-forgot .form-control,
.for-login-with-email-link .form-control, .for-signup .form-control {
    background: transparent !important;
    border: none !important;
    border-bottom: 1.5px solid var(--bl-underline) !important;
    border-radius: 0 !important;
    padding: 8px 8px 8px 26px !important;
    font-size: 14px !important;
    color: var(--bl-input-text) !important;
    box-shadow: none !important;
    height: auto !important;
    line-height: 1.5 !important;
    text-align: left;
}
.for-login .form-control:focus, .for-forgot .form-control:focus {
    border-bottom-color: var(--bl-underline-focus) !important;
    box-shadow: none !important;
    outline: 0 !important;
    background: transparent !important;
}
.for-login .form-control::placeholder { color: #8A96A5; opacity: 0.7; }
.form-group { margin-bottom: 6px !important; }
.email-field, .password-field { position: relative; }
.email-field .field-icon, .password-field .field-icon {
    position: absolute; left: 2px; top: 50%; transform: translateY(-50%);
    color: #8A96A5;
}
.password-field .toggle-password {
    position: absolute; right: 2px; top: 50%; transform: translateY(-50%);
    font-size: 12px; cursor: pointer; color: #8A96A5;
}
.forgot-password-message {
    text-align: right; font-size: 12px; margin: 6px 2px 12px !important;
}
.forgot-password-message a { color: #8A96A5; text-decoration: none; }
.forgot-password-message a:hover { color: var(--bl-nav-2); }

/* Login button — brand green/navy split, compact */
.btn-login, .btn.btn-primary.btn-login {
    {% if bl.btn_use_diagonal %}
    background: linear-gradient(90deg,
        var(--bl-btn-1) 0%, var(--bl-btn-1) 60%,
        var(--bl-btn-2) 60%, var(--bl-btn-2) 100%) !important;
    {% else %}
    background: var(--bl-btn-1) !important;
    {% endif %}
    color: var(--bl-btn-text) !important;
    border: 0 !important;
    border-radius: 30px !important;
    padding: 10px 20px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.04em;
    box-shadow: 0 4px 12px rgba(23,48,77,0.15) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    width: 100%;
}
.btn-login:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(23,48,77,0.22) !important; }

/* Extras inside card */
.brand-login-extras { padding-top: 14px; margin-top: 14px; border-top: 1px solid rgba(0,0,0,0.05); }
.brand-login-terms {
    text-align:center; color:var(--bl-terms-text);
    font-size:11.5px; line-height:1.5;
    padding:0 4px 8px; font-weight: 400;
}
.brand-login-terms a { color: var(--bl-terms-text); text-decoration: underline; }
.brand-login-powered { text-align:center; margin: 4px 0 8px; }
.brand-login-powered a { color:#2F80ED; font-weight:600; font-size:12.5px; text-decoration:none; }
.brand-login-powered a:hover { text-decoration: underline; }
.brand-login-social {
    display:flex; justify-content:center; gap:14px;
    color:#A17B47; padding-top:4px;
}
.brand-login-social a {
    color:#A17B47; transition: transform 0.15s, color 0.15s;
    display:inline-flex; align-items:center; justify-content:center;
    width: 26px; height: 26px;
}
.brand-login-social a:hover { color: var(--bl-nav-2); transform: translateY(-2px); }

.sign-up-message { color: #5A6B80; margin-top: 12px; font-size: 12.5px; }
.sign-up-message a { color: var(--bl-nav-2); font-weight: 600; }
.social-logins .btn { border-radius: 999px !important; height: 40px; }
.login-divider { color: #A0A8B5; margin: 10px 0 8px; font-size: 12px; }

/* Footer strip */
footer.web-footer { display: none !important; }
{% if completely_hide_footer_from_login_page %}.brand-login-footer { display: none !important; }{% endif %}
.brand-login-footer {
    {% if bl.footer_use_diagonal %}
    background: linear-gradient(105deg,
        var(--bl-foot-1) 0%, var(--bl-foot-1) 55%,
        var(--bl-foot-2) 60%, var(--bl-foot-2) 100%) !important;
    {% else %}
    background: var(--bl-foot-1) !important;
    {% endif %}
    color: var(--bl-foot-text);
    min-height: 60px; padding: 18px 28px; margin-top: auto;
    display: flex; align-items: center; font-weight: 500;
    font-size: 13px;
}

/* Responsive */
@media (max-width: 992px) {
    .navbar { min-height: 54px !important; padding: 0 16px !important; }
    .navbar-brand img, .navbar .app-logo { max-height: 32px !important; }
    .navbar::after { font-size: 15px; right: 18px; }
    .for-login .page-card, .for-forgot .page-card, .for-email-login .page-card {
        max-width: 92% !important; margin: 26px auto !important; padding: 24px 22px 18px !important;
    }
    .brand-login-footer { padding: 14px 18px; font-size: 12px; min-height: 52px; }
}
@media (max-width: 576px) {
    .navbar { min-height: 48px !important; padding: 0 12px !important; }
    .navbar-brand img, .navbar .app-logo { max-height: 28px !important; }
    .navbar::after { font-size: 13px; right: 12px; letter-spacing: 0; }
    .for-login .page-card, .for-forgot .page-card, .for-email-login .page-card {
        max-width: calc(100vw - 20px) !important;
        margin: 16px 10px !important;
        padding: 20px 16px 16px !important;
        border-radius: 12px !important;
    }
    .page-card-head img.app-logo { max-height: 38px; margin-bottom: 6px; }
    .page-card-head .brand-heading { font-size: 14px !important; }
    .page-card-head .brand-subtitle { font-size: 10px; }
    .for-login .form-control { font-size: 13px !important; padding: 7px 8px 7px 24px !important; }
    .btn-login { padding: 9px 18px !important; font-size: 13px !important; }
    .brand-login-terms { font-size: 11px; }
    .brand-login-powered a { font-size: 12px; }
    .brand-login-social { gap: 12px; }
    .brand-login-footer { padding: 12px 12px; font-size: 11.5px; min-height: 46px; text-align: center; justify-content: center; }
}
</style>
{% endblock %}

{% block footer %}
<footer class="brand-login-footer">
    <div class="copyright-text">{{ brand_login.copyright_text or "" }}</div>
</footer>
{% endblock %}

{% block page_content %}
<div>
    <noscript>
        <div class="text-center my-5">
            <h4>{{ _("Javascript is disabled on your browser") }}</h4>
            <p class="text-muted">{{ _("You need to enable JavaScript for your app to work.") }}</p>
        </div>
    </noscript>

    <section class='for-login'>
        <div class="login-content page-card">
            {{ logo_section() }}
            <form class="form-signin form-login" role="form">
                {%- if social_login or login_with_email_link -%}
                    {{ email_login_body() }}
                    <div class="social-logins text-center">
                        {% if not disable_user_pass_login or (ldap_settings and ldap_settings.enabled) %}
                        <p class="text-muted login-divider">{{ _("or") }}</p>{% endif %}
                        <div class="social-login-buttons">
                        {% for provider in provider_logins %}
                            <div class="login-button-wrapper">
                                <a href="{{ provider.auth_url }}" class="btn btn-block btn-default btn-sm btn-login-option btn-{{ provider.name }}">
                                {% if provider.icon %}{{ provider.icon }}{% endif %}
                                {{ _("Login with {0}").format(provider.provider_name) }}</a>
                            </div>
                        {% endfor %}
                        </div>
                    </div>
                {%- else -%}
                    {{ email_login_body() }}
                {%- endif -%}
            </form>
            {{ brand_card_extras() }}
        </div>
        {%- if not disable_signup and not disable_user_pass_login -%}
        <div class="text-center sign-up-message">
            {{ _("Don't have an account?") }} <a href="#signup">{{ _("Sign up") }}</a>
        </div>{%- endif -%}
    </section>

    {%- if social_login -%}
    <section class='for-email-login'>
        <div class="login-content page-card">
            {{ logo_section() }}
            <form class="form-signin form-login" role="form">{{ email_login_body() }}</form>
            {{ brand_card_extras() }}
        </div>
    </section>{%- endif -%}

    <section class='for-signup {{ "signup-disabled" if disable_signup else "" }}'>
        <div class="login-content page-card">
            {{ logo_section(_('Create a {0} Account').format(app_name or _("Framework"))) }}
            {%- if not disable_signup -%}{{ signup_form_template }}
            {%- else -%}
            <div class='page-card-head mb-2'>
                <span class='indicator gray'>{{ _("Signup Disabled") }}</span>
                <p class="text-muted text-normal sign-up-message mt-1 mb-8">{{ _("Signups have been disabled for this website.") }}</p>
                <div><a href='/' class='btn btn-primary btn-md'>{{ _("Home") }}</a></div>
            </div>{%- endif -%}
        </div>
    </section>

    <section class='for-forgot'>
        <div class="login-content page-card">
            {{ logo_section('Forgot Password') }}
            <form class="form-signin form-forgot hide" role="form">
                <div class="page-card-body">
                    <div class="email-field">
                        <input type="email" id="forgot_email" class="form-control" placeholder="{{ _('Email Address') }}" required autofocus autocomplete="username">
                    </div>
                </div>
                <div class="page-card-actions">
                    <button class="btn btn-sm btn-primary btn-block btn-forgot btn-login" type="submit">{{ _("Reset Password") }}</button>
                    <p class="text-center sign-up-message"><a href="#login">{{ _("Back to Login") }}</a></p>
                </div>
            </form>
        </div>
    </section>

    <section class='for-login-with-email-link'>
        <div class="login-content page-card">
            {{ logo_section(_('Login with Email Link')) }}
            <form class="form-signin form-login-with-email-link hide" role="form">
                <div class="page-card-body">
                    <div class="email-field">
                        <input type="email" id="login_with_email_link_email" class="form-control" placeholder="{{ _('Email Address') }}" required autofocus autocomplete="username">
                    </div>
                </div>
                <div class="page-card-actions">
                    <button class="btn btn-sm btn-primary btn-block btn-login-with-email-link btn-login" type="submit">{{ _("Send login link") }}</button>
                    <p class="text-center sign-up-message"><a href="#login">{{ _("Back to Login") }}</a></p>
                </div>
            </form>
        </div>
    </section>
</div>
{% endblock %}

{% block script %}
<script>{% include "templates/includes/login/login.js" %}</script>
{% if apply_image_or_color == "Slider" and background_slider_images %}
<script>
document.addEventListener("DOMContentLoaded", function () {
    let images = {{ background_slider_images | tojson }};
    let index = 0; let body = document.querySelector("body");
    let interval = ({{ interval or 5 }}) * 1000; let transition = {{ transition or 0.6 }} * 1000;
    if (images.length > 1) setInterval(() => { index=(index+1)%images.length; body.style.backgroundImage=`url('${images[index]}')`; }, interval + transition);
});
</script>{% endif %}
{% endblock %}

{% block sidebar %}{% endblock %}
"""


# =====================================================
# LOGIN PY (unchanged from Patch 04 — already fully dynamic)
# =====================================================
LOGIN_PY = r'''# Patched by Portal Theme pt_patcher (Patch 05)
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
    copyright_default = website_copyright or f"© {year} {app_name}."
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
'''


# =====================================================
# NAVBAR JS (unchanged)
# =====================================================
NAV_JS_BEGIN = "// === PT-NAVBAR-BRAND-FIX BEGIN ==="
NAV_JS_END   = "// === PT-NAVBAR-BRAND-FIX END ==="
NAV_JS_BLOCK = NAV_JS_BEGIN + """
(function () {
    function ptEnhanceNavbarBrand() {
        var links = document.querySelectorAll('.navbar-brand, header .app-logo-container a, .navbar .app-logo, .navbar-home');
        links.forEach(function (a) {
            if (a.dataset.ptBrandDone) return;
            a.dataset.ptBrandDone = '1';
            if (a.tagName === 'A') {
                var href = a.getAttribute('href');
                if (!href || href === '#' || href === '#/') a.setAttribute('href', '/app');
                a.addEventListener('click', function (e) {
                    if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) {
                        e.stopImmediatePropagation();
                        window.open(a.href, '_blank', 'noopener'); e.preventDefault();
                    }
                }, true);
                a.addEventListener('auxclick', function (e) {
                    if (e.button === 1) {
                        e.stopImmediatePropagation();
                        window.open(a.href, '_blank', 'noopener'); e.preventDefault();
                    }
                }, true);
            }
        });
    }
    if (document.readyState !== 'loading') ptEnhanceNavbarBrand();
    else document.addEventListener('DOMContentLoaded', ptEnhanceNavbarBrand);
    window.addEventListener('load', ptEnhanceNavbarBrand);
    setTimeout(ptEnhanceNavbarBrand, 800);
    setTimeout(ptEnhanceNavbarBrand, 2500);
})();
""" + NAV_JS_END + "\n"

def _inject_navbar_js():
    if not os.path.exists(PORTAL_JS_PATH): return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    current = re.sub(re.escape(NAV_JS_BEGIN)+r".*?"+re.escape(NAV_JS_END)+r"\n?", "", current, flags=re.DOTALL)
    with open(PORTAL_JS_PATH, "w") as f: f.write(current.rstrip()+"\n\n"+NAV_JS_BLOCK)

def _strip_navbar_js():
    if not os.path.exists(PORTAL_JS_PATH): return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    new = re.sub(re.escape(NAV_JS_BEGIN)+r".*?"+re.escape(NAV_JS_END)+r"\n?", "", current, flags=re.DOTALL).rstrip()+"\n"
    with open(PORTAL_JS_PATH, "w") as f: f.write(new)


# =====================================================
# APPLY / ROLLBACK
# =====================================================
def apply_02():
    if not os.path.isdir(APP_WWW_DIR):
        print(f">>> ERROR: {APP_WWW_DIR} not found"); return
    _ensure_original_file(LOGIN_HTML_PATH, "login.html")
    _ensure_original_file(LOGIN_PY_PATH,   "login.py")
    _timestamp_backup_file(LOGIN_HTML_PATH, "before_login.html")
    _timestamp_backup_file(LOGIN_PY_PATH,   "before_login.py")
    _add_custom_fields()
    _set_login_visual_defaults()
    with open(LOGIN_HTML_PATH, "w") as f: f.write(LOGIN_HTML)
    print(f"[write] {LOGIN_HTML_PATH}")
    with open(LOGIN_PY_PATH, "w") as f: f.write(LOGIN_PY)
    print(f"[write] {LOGIN_PY_PATH}")
    frappe.db.commit(); frappe.clear_cache()

def rollback_02():
    orig_html = os.path.join(BACKUP_DIR, "_ORIGINAL_login.html")
    orig_py   = os.path.join(BACKUP_DIR, "_ORIGINAL_login.py")
    if not os.path.exists(orig_html) or not os.path.exists(orig_py):
        print(">>> Missing originals"); return
    _timestamp_backup_file(LOGIN_HTML_PATH, "before_ROLLBACK_login.html")
    _timestamp_backup_file(LOGIN_PY_PATH,   "before_ROLLBACK_login.py")
    shutil.copy2(orig_html, LOGIN_HTML_PATH); shutil.copy2(orig_py, LOGIN_PY_PATH)
    _remove_custom_fields()
    frappe.db.commit(); frappe.clear_cache()
    print("[done] login rolled back.")


def apply_05_fixes():
    """Patch 05: compact v14 login + sidebar gap fix + status pill fix +
       light yellow field bg + reset old hardcoded strings."""
    print(">>> Applying Patch 05 fixes...")
    _ensure_original_file(PORTAL_JS_PATH, "portal_theme.js")
    _timestamp_backup_file(PORTAL_JS_PATH, "before_05_portal_theme.js")

    # Clear old hardcoded strings BEFORE applying (so users see the new dynamic behavior)
    _reset_old_hardcoded()

    # Baseline (desk) with all fixes
    apply_01_v2()

    # Login (compact v14 style)
    apply_02()

    # Navbar Ctrl-click
    _inject_navbar_js()

    frappe.db.commit(); frappe.clear_cache()
    print("")
    print("[done] Patch 05 applied.")
    print("       NOW RUN:  bench restart")
    print("       THEN hard-refresh /app and /login (Ctrl+Shift+R).")


def rollback_05_fixes():
    _strip_navbar_js()
    print("[done] navbar JS stripped.")
    print("       For a full revert:")
    print("         bench --site $SITE execute portal_theme.pt_patcher.rollback_02")
    print("         bench --site $SITE execute portal_theme.pt_patcher.rollback_01_v2")


# =====================================================
# PATCH 06 — Sidebar hover/select visibility fix ONLY
# =====================================================
SIDEBAR_MARKER_BEGIN = "/* PT-PATCH:06-sidebar BEGIN */"
SIDEBAR_MARKER_END   = "/* PT-PATCH:06-sidebar END */"

SIDEBAR_OVERRIDE_CSS = SIDEBAR_MARKER_BEGIN + """
/* Override sidebar hover/selected: keep text visible (no color changes),
   just add a translucent glass layer + green left rail on selected. */

/* HOVER — translucent white overlay, text stays as-is */
.body-sidebar .sidebar-item:hover,
.body-sidebar .standard-sidebar-item:hover,
.body-sidebar .desk-sidebar-item:hover,
.desk-sidebar .sidebar-item:hover,
.desk-sidebar .standard-sidebar-item:hover,
.desk-sidebar-item.standard-sidebar-item:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}
.body-sidebar .sidebar-item:hover *,
.desk-sidebar-item.standard-sidebar-item:hover * {
    color: #FFFFFF !important;
    background: transparent !important;
}

/* SELECTED — brighter translucent + 3px green left rail. Text stays visible. */
.body-sidebar .sidebar-item.selected,
.body-sidebar .standard-sidebar-item.selected,
.body-sidebar .desk-sidebar-item.selected,
.body-sidebar .sidebar-item.active,
.desk-sidebar .sidebar-item.selected,
.desk-sidebar .standard-sidebar-item.selected,
.desk-sidebar-item.standard-sidebar-item.selected,
.desk-sidebar-item.selected,
.body-sidebar [aria-current="page"] {
    background: rgba(255,255,255,0.14) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-left: 3px solid #3ECF57 !important;
    padding-left: 9px !important;
    border-radius: 0 4px 4px 0 !important;
}
.body-sidebar .sidebar-item.selected *,
.body-sidebar .standard-sidebar-item.selected *,
.desk-sidebar-item.standard-sidebar-item.selected *,
.desk-sidebar-item.selected * {
    color: #FFFFFF !important;
    background: transparent !important;
}

/* Selected item hover — slightly brighter, keep rail */
.body-sidebar .sidebar-item.selected:hover,
.desk-sidebar-item.standard-sidebar-item.selected:hover {
    background: rgba(255,255,255,0.20) !important;
}
""" + SIDEBAR_MARKER_END + "\n"


def apply_06_sidebar():
    """Patch 06: only fixes sidebar hover/selected visibility.
       Adds a marker block AFTER the baseline so it wins the cascade."""
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_06_sidebar")

    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Remove any prior copy of this specific patch
    current = re.sub(
        re.escape(SIDEBAR_MARKER_BEGIN) + r".*?" + re.escape(SIDEBAR_MARKER_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()

    new_css = current + "\n\n" + SIDEBAR_OVERRIDE_CSS
    _save_css(new_css)
    print("[done] Patch 06 sidebar fix applied. Hard-refresh browser (Ctrl+Shift+R).")


def rollback_06_sidebar():
    """Removes only the Patch 06 block; leaves everything else intact."""
    _timestamp_backup_css("before_ROLLBACK_06_sidebar")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(SIDEBAR_MARKER_BEGIN) + r".*?" + re.escape(SIDEBAR_MARKER_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 06 rolled back.")


# =====================================================
# PATCH 07 — Sidebar spacing + brighter text (nuclear override)
# =====================================================
SIDEBAR_07_BEGIN = "/* PT-PATCH:07-sidebar-tight BEGIN */"
SIDEBAR_07_END   = "/* PT-PATCH:07-sidebar-tight END */"

SIDEBAR_07_CSS = SIDEBAR_07_BEGIN + """
/* -------- Sidebar spacing: zero everything, then set one clean value -------- */

/* Every wrapper: zero margins/padding */
.body-sidebar,
.body-sidebar-container,
.desk-sidebar,
.layout-side-section {
    padding: 8px 4px !important;
}

.body-sidebar ul, .body-sidebar ol,
.desk-sidebar ul, .desk-sidebar ol,
.body-sidebar-container ul, .body-sidebar-container ol,
.body-sidebar .list-unstyled,
.desk-sidebar .list-unstyled {
    margin: 0 !important;
    padding: 0 !important;
    list-style: none !important;
    gap: 0 !important;
    row-gap: 0 !important;
}
.body-sidebar li,
.desk-sidebar li,
.body-sidebar-container li {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    list-style: none !important;
}

/* The actual item elements */
.body-sidebar .sidebar-item,
.body-sidebar .standard-sidebar-item,
.body-sidebar .desk-sidebar-item,
.desk-sidebar .sidebar-item,
.desk-sidebar .standard-sidebar-item,
.desk-sidebar-item.standard-sidebar-item,
.body-sidebar a.sidebar-item,
.desk-sidebar a.sidebar-item {
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 5px 12px !important;
    line-height: 1.35 !important;
    min-height: 0 !important;
    border-radius: 4px !important;
    color: #F1F5FA !important;
    background: transparent !important;
    text-decoration: none !important;
    transition: background 0.12s ease !important;
}

/* Children — brighter, no self-padding, no line breaks */
.body-sidebar .sidebar-item *,
.body-sidebar .standard-sidebar-item *,
.desk-sidebar-item.standard-sidebar-item * {
    color: #F1F5FA !important;
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: inherit !important;
}
.body-sidebar .sidebar-item .sidebar-item-icon,
.body-sidebar .sidebar-item svg,
.desk-sidebar-item.standard-sidebar-item .sidebar-item-icon,
.desk-sidebar-item.standard-sidebar-item svg {
    margin-right: 10px !important;
    flex-shrink: 0;
}
.body-sidebar .sidebar-item .sidebar-item-label,
.body-sidebar .sidebar-item .item-label,
.desk-sidebar-item.standard-sidebar-item .sidebar-item-label {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Hover — translucent glass, brighter text */
.body-sidebar .sidebar-item:hover,
.body-sidebar .standard-sidebar-item:hover,
.body-sidebar .desk-sidebar-item:hover,
.desk-sidebar .sidebar-item:hover,
.desk-sidebar .standard-sidebar-item:hover,
.desk-sidebar-item.standard-sidebar-item:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}
.body-sidebar .sidebar-item:hover *,
.desk-sidebar-item.standard-sidebar-item:hover * {
    color: #FFFFFF !important;
}

/* Selected — brighter glass + green left rail */
.body-sidebar .sidebar-item.selected,
.body-sidebar .standard-sidebar-item.selected,
.body-sidebar .desk-sidebar-item.selected,
.body-sidebar .sidebar-item.active,
.desk-sidebar .sidebar-item.selected,
.desk-sidebar .standard-sidebar-item.selected,
.desk-sidebar-item.standard-sidebar-item.selected,
.desk-sidebar-item.selected,
.body-sidebar [aria-current="page"] {
    background: rgba(255,255,255,0.14) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-left: 3px solid #3ECF57 !important;
    padding-left: 9px !important;
    border-radius: 0 4px 4px 0 !important;
}
.body-sidebar .sidebar-item.selected *,
.body-sidebar .standard-sidebar-item.selected *,
.desk-sidebar-item.standard-sidebar-item.selected *,
.desk-sidebar-item.selected * {
    color: #FFFFFF !important;
}
.body-sidebar .sidebar-item.selected:hover,
.desk-sidebar-item.standard-sidebar-item.selected:hover {
    background: rgba(255,255,255,0.20) !important;
}

/* Section titles (Setup, Opening & Closing…) — subtle uppercase caption */
.body-sidebar .standard-sidebar-section .sidebar-section-title,
.body-sidebar .standard-sidebar-section-title,
.desk-sidebar .standard-sidebar-section-title {
    color: rgba(255,255,255,0.55) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 8px 12px 2px !important;
    margin: 0 !important;
    font-weight: 600 !important;
}

/* Group expand/collapse chevron rows shouldn't add extra padding either */
.body-sidebar .sidebar-child-item,
.desk-sidebar .sidebar-child-item {
    margin: 0 !important; padding: 0 !important;
}
""" + SIDEBAR_07_END + "\n"


def apply_07_sidebar_tight():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_07_sidebar_tight")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""

    # Also remove Patch 06 block if present (this one supersedes it)
    current = re.sub(
        r"/\* PT-PATCH:06-sidebar BEGIN \*/.*?/\* PT-PATCH:06-sidebar END \*/\n?",
        "", current, flags=re.DOTALL,
    )
    # Remove any prior Patch 07
    current = re.sub(
        re.escape(SIDEBAR_07_BEGIN) + r".*?" + re.escape(SIDEBAR_07_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()

    new_css = current + "\n\n" + SIDEBAR_07_CSS
    _save_css(new_css)
    print("[done] Patch 07 sidebar-tight applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_07_sidebar_tight():
    _timestamp_backup_css("before_ROLLBACK_07_sidebar_tight")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(SIDEBAR_07_BEGIN) + r".*?" + re.escape(SIDEBAR_07_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 07 rolled back.")


# =====================================================
# PATCH 08 — Login footer bar text = Website Settings.copyright only
# =====================================================
def apply_08_footer_from_website_settings():
    """Ensure the login footer bar text is ALWAYS pulled from
       Website Settings → copyright. No fallback, no hardcode."""

    # 1) Clear any value the user (or a prior patch) put in login_copyright_text
    if frappe.db.exists("Custom Field", "Portal Theme Setting-login_copyright_text"):
        frappe.db.set_value("Portal Theme Setting", "Portal Theme Setting",
                            "login_copyright_text", "")
        print("[clear] login_copyright_text set to empty (will fetch from Website Settings)")

    # 2) Patch login.py so copyright_text falls back to '' (not auto-built) when both fields are empty
    if not os.path.exists(LOGIN_PY_PATH):
        print(f">>> ERROR: {LOGIN_PY_PATH} not found"); return

    _timestamp_backup_file(LOGIN_PY_PATH, "before_08_login.py")

    with open(LOGIN_PY_PATH, "r") as f:
        py = f.read()

    # Replace the copyright_default line to drop the auto-built fallback
    py_new = re.sub(
        r'copyright_default\s*=\s*website_copyright\s+or\s+f"© \{year\} \{app_name\}\."',
        'copyright_default = website_copyright  # Patch 08: Website Settings.copyright ONLY',
        py,
    )

    if py_new == py:
        # Line already patched or template moved; do a broader match
        py_new = re.sub(
            r'copyright_default\s*=\s*[^\n]+',
            'copyright_default = website_copyright  # Patch 08: Website Settings.copyright ONLY',
            py,
        )

    with open(LOGIN_PY_PATH, "w") as f:
        f.write(py_new)
    print(f"[write] {LOGIN_PY_PATH} — copyright_default now Website Settings only")

    frappe.db.commit()
    frappe.clear_cache()
    print("")
    print("[done] Patch 08 applied.")
    print("       Set the text at: /app/website-settings → Copyright field")
    print("       NOW RUN:  bench restart")
    print("       THEN hard-refresh /login (Ctrl+Shift+R).")


def rollback_08_footer_from_website_settings():
    """Restore Patch 05's original copyright_default line
       (Website Settings OR auto-built '© {year} {app_name}.')."""
    if not os.path.exists(LOGIN_PY_PATH):
        print(f">>> {LOGIN_PY_PATH} not found"); return

    _timestamp_backup_file(LOGIN_PY_PATH, "before_ROLLBACK_08_login.py")

    with open(LOGIN_PY_PATH, "r") as f:
        py = f.read()

    py_new = re.sub(
        r'copyright_default\s*=\s*website_copyright\s*#[^\n]*',
        'copyright_default = website_copyright or f"© {year} {app_name}."',
        py,
    )
    with open(LOGIN_PY_PATH, "w") as f:
        f.write(py_new)
    print(f"[restore] {LOGIN_PY_PATH} — auto-built fallback restored")

    frappe.db.commit()
    frappe.clear_cache()
    print("[done] Patch 08 rolled back. Run: bench restart")


# =====================================================
# PATCH 09 — Login footer auto-prefixes © and year, like ERPNext web footer
# =====================================================
def apply_09_footer_copyright_symbol():
    """Match ERPNext's standard web footer behavior:
       Website Settings.copyright = 'Baarjeex Group of Companies.'
       Rendered footer                = '© 2026 Baarjeex Group of Companies.'
       The © and year are always auto-prepended in the template."""

    # Clear any override on the Portal Theme Setting so we always fall through
    # to the auto-formatted default.
    if frappe.db.exists("Custom Field", "Portal Theme Setting-login_copyright_text"):
        frappe.db.set_value("Portal Theme Setting", "Portal Theme Setting",
                            "login_copyright_text", "")
        print("[clear] login_copyright_text emptied")

    if not os.path.exists(LOGIN_PY_PATH):
        print(f">>> ERROR: {LOGIN_PY_PATH} not found"); return

    _timestamp_backup_file(LOGIN_PY_PATH, "before_09_login.py")

    with open(LOGIN_PY_PATH, "r") as f:
        py = f.read()

    # Match ANY previous copyright_default line and replace with the new formula
    new_line = 'copyright_default = f"© {year} {website_copyright}" if website_copyright else ""  # Patch 09: auto © and year'
    py_new, n = re.subn(
        r'copyright_default\s*=\s*[^\n]+',
        new_line,
        py,
    )

    if n == 0:
        print(">>> WARN: could not locate copyright_default line in login.py. Aborting.")
        return

    with open(LOGIN_PY_PATH, "w") as f:
        f.write(py_new)
    print(f"[write] {LOGIN_PY_PATH} — copyright now auto-prefixes © and year")

    frappe.db.commit()
    frappe.clear_cache()
    print("")
    print("[done] Patch 09 applied.")
    print("       In /app/website-settings, put ONLY the company text in Copyright,")
    print("       e.g.  'Baarjeex Group of Companies.'  (no © needed).")
    print("       The login footer will render:  '© 2026 Baarjeex Group of Companies.'")
    print("")
    print("       NOW RUN:  bench restart")
    print("       THEN hard-refresh /login (Ctrl+Shift+R).")


def rollback_09_footer_copyright_symbol():
    if not os.path.exists(LOGIN_PY_PATH):
        print(f">>> {LOGIN_PY_PATH} not found"); return
    _timestamp_backup_file(LOGIN_PY_PATH, "before_ROLLBACK_09_login.py")
    with open(LOGIN_PY_PATH, "r") as f:
        py = f.read()
    py_new = re.sub(
        r'copyright_default\s*=\s*[^\n]+',
        'copyright_default = website_copyright or f"© {year} {app_name}."',
        py,
    )
    with open(LOGIN_PY_PATH, "w") as f:
        f.write(py_new)
    frappe.db.commit(); frappe.clear_cache()
    print("[done] Patch 09 rolled back. Run: bench restart")


# =====================================================
# PATCH 10 — Workspace shortcut pills + link cards
# =====================================================
WS10_BEGIN = "/* PT-PATCH:10-workspace-cards BEGIN */"
WS10_END   = "/* PT-PATCH:10-workspace-cards END */"

WS10_CSS = WS10_BEGIN + """
/* -------- Shortcut pills (Your Shortcuts row) -------- */
.widget.shortcut-widget-box,
.shortcut-widget-box {
    background: #D3DEEE !important;
    background-image: none !important;
    border: 0 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    padding: 14px 16px !important;
    min-height: auto !important;
    color: #1B2431 !important;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.widget.shortcut-widget-box:hover,
.shortcut-widget-box:hover {
    background: #C5D3E7 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    transform: none !important;
}
.widget.shortcut-widget-box .widget-title,
.widget.shortcut-widget-box .widget-title *,
.widget.shortcut-widget-box .ellipsis,
.shortcut-widget-box .widget-title,
.shortcut-widget-box .ellipsis {
    color: #1B2431 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* -------- Link cards (Accounting / Stock / CRM / Data Import…) -------- */
.widget.links-widget-box,
.links-widget-box {
    background: #EEF1F5 !important;
    background-image: linear-gradient(135deg, #EEF1F5 0%, #EEF1F5 68%, #D9E3EE 100%) !important;
    border: 0 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    padding: 22px 24px !important;
    color: #1B2431 !important;
    transition: box-shadow 0.15s ease;
}
.widget.links-widget-box:hover,
.links-widget-box:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    transform: none !important;
}
.widget.links-widget-box .widget-head,
.widget.links-widget-box .widget-title,
.widget.links-widget-box .widget-title *,
.widget.links-widget-box .ellipsis,
.links-widget-box .widget-head,
.links-widget-box .widget-title {
    color: #1B2431 !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
    background: transparent !important;
}
.widget.links-widget-box .link-item,
.widget.links-widget-box .link-item *,
.widget.links-widget-box .widget-body a,
.links-widget-box .link-item,
.links-widget-box a {
    color: #1B2431 !important;
    padding: 4px 0 !important;
    text-decoration: none !important;
    font-size: 14px !important;
    background: transparent !important;
}
.widget.links-widget-box .link-item:hover,
.links-widget-box a:hover {
    color: #17304D !important;
    text-decoration: underline !important;
}
""" + WS10_END + "\n"


def apply_10_workspace_cards():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_10_workspace_cards")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Idempotent: remove any prior copy of this exact patch first
    current = re.sub(
        re.escape(WS10_BEGIN) + r".*?" + re.escape(WS10_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + WS10_CSS
    _save_css(new_css)
    print("[done] Patch 10 workspace-cards applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_10_workspace_cards():
    _timestamp_backup_css("before_ROLLBACK_10_workspace_cards")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(WS10_BEGIN) + r".*?" + re.escape(WS10_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 10 rolled back — workspace cards return to previous state.")


# =====================================================
# PATCH 11 — Workspace cards: exact gradient + tight arrow rows
# =====================================================
WS11_BEGIN = "/* PT-PATCH:11-workspace-cards-v2 BEGIN */"
WS11_END   = "/* PT-PATCH:11-workspace-cards-v2 END */"

WS11_CSS = WS11_BEGIN + """
/* ---- Shortcut pills (Your Shortcuts row) ---- */
.widget.shortcut-widget-box,
.shortcut-widget-box {
    background: #D3DEEE !important;
    background-image: none !important;
    border: 0 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    padding: 14px 16px !important;
    min-height: auto !important;
    color: #1B2431 !important;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.widget.shortcut-widget-box:hover,
.shortcut-widget-box:hover {
    background: #C5D3E7 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    transform: none !important;
}
.widget.shortcut-widget-box .widget-title,
.widget.shortcut-widget-box .widget-title *,
.widget.shortcut-widget-box .ellipsis {
    color: #1B2431 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* ---- Link cards (Accounting / Stock / CRM / Data Import…) ---- */
.widget.links-widget-box,
.links-widget-box {
    background: linear-gradient(110deg, #eceef3 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #eceef3 90%, #d4e1f0 70%) !important;
    border: 0 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    padding: 20px 22px !important;
    color: #1B2431 !important;
    transition: box-shadow 0.15s ease;
}
.widget.links-widget-box:hover,
.links-widget-box:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    transform: none !important;
}

/* Card title */
.widget.links-widget-box .widget-head,
.widget.links-widget-box .widget-title,
.widget.links-widget-box .widget-title * {
    color: #1B2431 !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    margin: 0 0 10px !important;
    padding: 0 !important;
    background: transparent !important;
    border-bottom: 0 !important;
}

/* Body — kill all gaps and inherited margins */
.widget.links-widget-box .widget-body,
.links-widget-box .widget-body {
    padding: 0 !important;
    margin: 0 !important;
    display: block !important;
}
.widget.links-widget-box .widget-body > *,
.links-widget-box .widget-body > * {
    margin: 0 !important;
    padding: 0 !important;
}
.widget.links-widget-box .widget-body ul,
.widget.links-widget-box .widget-body ol,
.links-widget-box .widget-body ul {
    list-style: none !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
    row-gap: 0 !important;
}
.widget.links-widget-box .widget-body li,
.links-widget-box .widget-body li {
    list-style: none !important;
    padding: 0 !important;
    margin: 0 !important;
    line-height: 1 !important;
}

/* Kill any bullet/dot pseudo-element Frappe injects */
.widget.links-widget-box .link-item::before,
.widget.links-widget-box .widget-body a::before,
.widget.links-widget-box .widget-body li::before,
.links-widget-box .widget-body ::before {
    content: none !important;
    display: none !important;
}

/* The actual link row */
.widget.links-widget-box .link-item,
.widget.links-widget-box .widget-body a,
.links-widget-box .link-item,
.links-widget-box .widget-body a {
    display: flex !important;
    align-items: center !important;
    gap: 6px;
    color: #1B2431 !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    text-decoration: none !important;
    background: transparent !important;
    padding: 3px 0 !important;
    margin: 0 !important;
    line-height: 1.35 !important;
    min-height: 0 !important;
    border: 0 !important;
}
.widget.links-widget-box .link-item:hover,
.widget.links-widget-box .widget-body a:hover,
.links-widget-box .link-item:hover,
.links-widget-box .widget-body a:hover {
    color: #17304D !important;
    text-decoration: underline !important;
    background: transparent !important;
}
.widget.links-widget-box .link-item *,
.widget.links-widget-box .widget-body a *,
.links-widget-box .link-item * {
    color: inherit !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Arrow icon (already in markup) — subtle, aligned with text */
.widget.links-widget-box .link-item svg,
.widget.links-widget-box .widget-body a svg,
.links-widget-box .link-item svg,
.links-widget-box .widget-body a svg {
    width: 12px !important;
    height: 12px !important;
    margin-left: 4px !important;
    color: #5A6B80 !important;
    opacity: 0.85;
    flex-shrink: 0;
}
""" + WS11_END + "\n"


def apply_11_workspace_cards_v2():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_11_workspace_cards_v2")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Remove Patch 10 if it's there (this supersedes it)
    current = re.sub(
        r"/\* PT-PATCH:10-workspace-cards BEGIN \*/.*?/\* PT-PATCH:10-workspace-cards END \*/\n?",
        "", current, flags=re.DOTALL,
    )
    # Remove any prior copy of Patch 11
    current = re.sub(
        re.escape(WS11_BEGIN) + r".*?" + re.escape(WS11_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + WS11_CSS
    _save_css(new_css)
    print("[done] Patch 11 workspace-cards-v2 applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_11_workspace_cards_v2():
    _timestamp_backup_css("before_ROLLBACK_11_workspace_cards_v2")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(WS11_BEGIN) + r".*?" + re.escape(WS11_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 11 rolled back.")


# =====================================================
# PATCH 12 — Dark mode fix for workspace cards + shortcuts
# =====================================================
WS12_BEGIN = "/* PT-PATCH:12-workspace-dark BEGIN */"
WS12_END   = "/* PT-PATCH:12-workspace-dark END */"

WS12_CSS = WS12_BEGIN + """
/* -------- DARK MODE — workspace shell -------- */
:root[data-theme="dark"] body,
:root[data-theme="dark"] .desk-page,
:root[data-theme="dark"] .layout-main,
:root[data-theme="dark"] .layout-main-section,
:root[data-theme="dark"] .workspace-body,
:root[data-theme="dark"] .page-container,
:root[data-theme="dark"] .page-body {
    background: #0D1929 !important;
    color: #E6EAF0 !important;
}

/* Section headings ("Your Shortcuts", "Reports & Masters") — light */
:root[data-theme="dark"] .workspace-body h1,
:root[data-theme="dark"] .workspace-body h2,
:root[data-theme="dark"] .workspace-body h3,
:root[data-theme="dark"] .workspace-body h4,
:root[data-theme="dark"] .workspace-body .section-head,
:root[data-theme="dark"] .workspace-body .widget-group-head,
:root[data-theme="dark"] .workspace-body .widget-group-title {
    color: #E6EAF0 !important;
}

/* -------- Shortcut pills — dark surface, brand-green text -------- */
:root[data-theme="dark"] .widget.shortcut-widget-box,
:root[data-theme="dark"] .shortcut-widget-box {
    background: #1E2A3E !important;
    background-image: none !important;
    color: #3ECF57 !important;
    border: 0 !important;
    box-shadow: none !important;
}
:root[data-theme="dark"] .widget.shortcut-widget-box:hover,
:root[data-theme="dark"] .shortcut-widget-box:hover {
    background: #263452 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.35) !important;
}
:root[data-theme="dark"] .widget.shortcut-widget-box .widget-title,
:root[data-theme="dark"] .widget.shortcut-widget-box .widget-title *,
:root[data-theme="dark"] .widget.shortcut-widget-box .ellipsis {
    color: #3ECF57 !important;
    font-weight: 500 !important;
}

/* -------- Link cards — dark version of the same gradient recipe -------- */
:root[data-theme="dark"] .widget.links-widget-box,
:root[data-theme="dark"] .links-widget-box {
    background: linear-gradient(110deg, #1A2436 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #1A2436 90%, #253753 70%) !important;
    color: #E6EAF0 !important;
    border: 0 !important;
    box-shadow: none !important;
}
:root[data-theme="dark"] .widget.links-widget-box:hover,
:root[data-theme="dark"] .links-widget-box:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.35) !important;
}

/* Title inside dark cards — brand green */
:root[data-theme="dark"] .widget.links-widget-box .widget-head,
:root[data-theme="dark"] .widget.links-widget-box .widget-title,
:root[data-theme="dark"] .widget.links-widget-box .widget-title * {
    color: #3ECF57 !important;
}

/* Row links — light text, arrow slightly muted */
:root[data-theme="dark"] .widget.links-widget-box .link-item,
:root[data-theme="dark"] .widget.links-widget-box .widget-body a,
:root[data-theme="dark"] .links-widget-box .link-item,
:root[data-theme="dark"] .links-widget-box .widget-body a {
    color: #E6EAF0 !important;
    background: transparent !important;
}
:root[data-theme="dark"] .widget.links-widget-box .link-item *,
:root[data-theme="dark"] .widget.links-widget-box .widget-body a * {
    color: inherit !important;
}
:root[data-theme="dark"] .widget.links-widget-box .link-item:hover,
:root[data-theme="dark"] .widget.links-widget-box .widget-body a:hover {
    color: #3ECF57 !important;
    text-decoration: underline !important;
}
:root[data-theme="dark"] .widget.links-widget-box .link-item svg,
:root[data-theme="dark"] .widget.links-widget-box .widget-body a svg {
    color: #A0AAB6 !important;
    opacity: 0.75;
}
""" + WS12_END + "\n"


def apply_12_workspace_dark():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_12_workspace_dark")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    current = re.sub(
        re.escape(WS12_BEGIN) + r".*?" + re.escape(WS12_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + WS12_CSS
    _save_css(new_css)
    print("[done] Patch 12 workspace-dark applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_12_workspace_dark():
    _timestamp_backup_css("before_ROLLBACK_12_workspace_dark")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(WS12_BEGIN) + r".*?" + re.escape(WS12_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 12 rolled back.")


# =====================================================
# PATCH 13 — Checkbox / radio / switch visibility
# =====================================================
CB13_BEGIN = "/* PT-PATCH:13-checkboxes BEGIN */"
CB13_END   = "/* PT-PATCH:13-checkboxes END */"

CB13_CSS = CB13_BEGIN + """
/* -------- Checkbox (unchecked) -------- */
input[type="checkbox"] {
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
    appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    min-width: 18px !important;
    min-height: 18px !important;
    border: 2px solid #A0AAB6 !important;
    border-radius: 4px !important;
    background: #FFFFFF !important;
    cursor: pointer;
    position: relative;
    display: inline-block;
    vertical-align: middle;
    margin: 0 6px 0 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    transition: background 0.12s ease, border-color 0.12s ease;
    flex-shrink: 0;
}

input[type="checkbox"]:hover {
    border-color: #17304D !important;
    background: #F7F9FC !important;
}

/* Focus ring (accessibility) */
input[type="checkbox"]:focus,
input[type="checkbox"]:focus-visible {
    outline: 0 !important;
    box-shadow: 0 0 0 3px rgba(62,207,87,0.35) !important;
}

/* Checked — solid green with white check */
input[type="checkbox"]:checked {
    background-color: #3ECF57 !important;
    border-color: #3ECF57 !important;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'><path d='M3 8.5l3.2 3.2L13 5' stroke='%23FFFFFF' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/></svg>") !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-size: 14px 14px !important;
}
input[type="checkbox"]:checked:hover {
    background-color: #2FB84A !important;
    border-color: #2FB84A !important;
}

/* Indeterminate state (partial-select) */
input[type="checkbox"]:indeterminate {
    background-color: #3ECF57 !important;
    border-color: #3ECF57 !important;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'><path d='M3 8h10' stroke='%23FFFFFF' stroke-width='2.4' stroke-linecap='round'/></svg>") !important;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 14px 14px;
}

/* Disabled */
input[type="checkbox"]:disabled {
    background: #EEF2F7 !important;
    border-color: #C7D0DB !important;
    cursor: not-allowed;
    opacity: 0.7;
}
input[type="checkbox"]:disabled:checked {
    background-color: #A0AAB6 !important;
    border-color: #A0AAB6 !important;
}

/* -------- Radio buttons -------- */
input[type="radio"] {
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
    appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    min-width: 18px !important;
    min-height: 18px !important;
    border: 2px solid #A0AAB6 !important;
    border-radius: 50% !important;
    background: #FFFFFF !important;
    cursor: pointer;
    position: relative;
    display: inline-block;
    vertical-align: middle;
    margin: 0 6px 0 0 !important;
    box-shadow: none !important;
    transition: border-color 0.12s ease;
    flex-shrink: 0;
}
input[type="radio"]:hover {
    border-color: #17304D !important;
}
input[type="radio"]:focus,
input[type="radio"]:focus-visible {
    outline: 0 !important;
    box-shadow: 0 0 0 3px rgba(62,207,87,0.35) !important;
}
input[type="radio"]:checked {
    border-color: #3ECF57 !important;
    background: radial-gradient(circle at center, #3ECF57 45%, #FFFFFF 50%) !important;
}
input[type="radio"]:disabled {
    background: #EEF2F7 !important;
    border-color: #C7D0DB !important;
    cursor: not-allowed;
    opacity: 0.7;
}

/* -------- Frappe toggle switch (Check field with Toggle option) -------- */
.frappe-control[data-fieldtype="Check"] .toggle-switch,
.control-input .toggle-switch {
    background: #C7D0DB !important;
    border-radius: 999px !important;
    transition: background 0.15s ease;
}
.frappe-control[data-fieldtype="Check"] .toggle-switch.on,
.control-input .toggle-switch.on {
    background: #3ECF57 !important;
}

/* -------- DARK MODE -------- */
:root[data-theme="dark"] input[type="checkbox"],
:root[data-theme="dark"] input[type="radio"] {
    background: #1A2436 !important;
    border-color: #4A5568 !important;
}
:root[data-theme="dark"] input[type="checkbox"]:hover,
:root[data-theme="dark"] input[type="radio"]:hover {
    background: #253753 !important;
    border-color: #8A96A5 !important;
}
:root[data-theme="dark"] input[type="checkbox"]:checked {
    background-color: #3ECF57 !important;
    border-color: #3ECF57 !important;
}
:root[data-theme="dark"] input[type="radio"]:checked {
    border-color: #3ECF57 !important;
    background: radial-gradient(circle at center, #3ECF57 45%, #1A2436 50%) !important;
}
:root[data-theme="dark"] input[type="checkbox"]:disabled,
:root[data-theme="dark"] input[type="radio"]:disabled {
    background: #253753 !important;
    border-color: #3A4558 !important;
}
""" + CB13_END + "\n"


def apply_13_checkboxes():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_13_checkboxes")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    current = re.sub(
        re.escape(CB13_BEGIN) + r".*?" + re.escape(CB13_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + CB13_CSS
    _save_css(new_css)
    print("[done] Patch 13 checkboxes applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_13_checkboxes():
    _timestamp_backup_css("before_ROLLBACK_13_checkboxes")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(CB13_BEGIN) + r".*?" + re.escape(CB13_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 13 rolled back.")


# =====================================================
# PATCH 14 — Checkbox: use ::after checkmark (SVG bg was failing)
# =====================================================
CB14_BEGIN = "/* PT-PATCH:14-check-tick BEGIN */"
CB14_END   = "/* PT-PATCH:14-check-tick END */"

CB14_CSS = CB14_BEGIN + """
/* Kill the SVG background from Patch 13 (it was rendering as a solid fill
   because the escaped SVG data URL didn't decode reliably in Frappe's
   context). Draw the tick with a rotated ::after pseudo instead. */

input[type="checkbox"] {
    position: relative !important;
    background-image: none !important;
}

input[type="checkbox"]:checked {
    background-color: #3ECF57 !important;
    border-color: #3ECF57 !important;
    background-image: none !important;
}

/* The checkmark itself — two-line CSS shape, rotated */
input[type="checkbox"]:checked::after {
    content: "" !important;
    position: absolute !important;
    left: 4px !important;
    top: 0px !important;
    width: 5px !important;
    height: 10px !important;
    border: solid #FFFFFF !important;
    border-width: 0 2.5px 2.5px 0 !important;
    transform: rotate(45deg) !important;
    display: block !important;
    box-sizing: border-box !important;
    background: transparent !important;
    pointer-events: none;
}

/* Indeterminate — horizontal white bar */
input[type="checkbox"]:indeterminate {
    background-color: #3ECF57 !important;
    border-color: #3ECF57 !important;
    background-image: none !important;
}
input[type="checkbox"]:indeterminate::after {
    content: "" !important;
    position: absolute !important;
    left: 3px !important;
    top: 6px !important;
    width: 8px !important;
    height: 2.5px !important;
    background: #FFFFFF !important;
    border: 0 !important;
    transform: none !important;
    border-radius: 1px;
    display: block !important;
    pointer-events: none;
}

/* Make sure the disabled-checked state greys out cleanly */
input[type="checkbox"]:disabled:checked {
    background-color: #A0AAB6 !important;
    border-color: #A0AAB6 !important;
}
""" + CB14_END + "\n"


def apply_14_check_tick():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_14_check_tick")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    current = re.sub(
        re.escape(CB14_BEGIN) + r".*?" + re.escape(CB14_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + CB14_CSS
    _save_css(new_css)
    print("[done] Patch 14 check-tick applied. Hard-refresh (Ctrl+Shift+R).")


def rollback_14_check_tick():
    _timestamp_backup_css("before_ROLLBACK_14_check_tick")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(CB14_BEGIN) + r".*?" + re.escape(CB14_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 14 rolled back.")


# =====================================================
# PATCH 15 — Desk home: hero band + grouped gradient tiles
#   Pure CSS + one JS injection into portal_theme.js.
#   Zero changes to Frappe/ERPNext source.
# =====================================================
DESK15_BEGIN = "/* PT-PATCH:15-desk-home BEGIN */"
DESK15_END   = "/* PT-PATCH:15-desk-home END */"

DESK15_CSS = DESK15_BEGIN + """
/* ============ HERO BAND (injected by JS at top of desk home) ============ */
.pt-desk-hero {
    background: #FFFFFF;
    border: 1px solid #E1E7EE;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 8px 0 22px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
}
.pt-desk-hero-left { min-width: 0; flex: 1; }
.pt-desk-hero-greeting {
    font-size: 16px;
    font-weight: 500;
    color: #17304D;
    margin: 0 0 4px;
    line-height: 1.3;
}
.pt-desk-hero-sub {
    font-size: 12.5px;
    color: #5A6B80;
    margin: 0;
}
.pt-desk-hero-actions {
    display: flex; gap: 8px; align-items: center; flex-shrink: 0;
}
.pt-desk-hero-actions .btn {
    border-radius: 999px !important;
    padding: 6px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: auto !important;
}

/* Dark mode hero */
:root[data-theme="dark"] .pt-desk-hero {
    background: #1A2436;
    border-color: #2A3548;
}
:root[data-theme="dark"] .pt-desk-hero-greeting { color: #E6EAF0; }
:root[data-theme="dark"] .pt-desk-hero-sub { color: #A0AAB6; }

/* ============ MODULE TILES (Frappe's own /app grid) ============ */
/* Frappe renders /app root as a grid of .module-icon anchors.
   We restyle them into gradient cards — no markup changes. */
.desk-page .module-body,
.layout-main-section .module-icons-container,
.container .modules-container {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
    gap: 14px !important;
    padding: 4px 0 !important;
    align-items: stretch !important;
}

/* Each tile */
.module-icons-container .module-icon,
.modules-container .module-icon,
.desk-page .module-icon,
a.module-icon {
    background: linear-gradient(110deg, #eceef3 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #eceef3 90%, #d4e1f0 70%) !important;
    border-radius: 12px !important;
    padding: 18px 18px !important;
    border: 0 !important;
    box-shadow: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    text-decoration: none !important;
    min-height: 100px !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
    color: #17304D !important;
}
.module-icons-container .module-icon:hover,
.modules-container .module-icon:hover,
a.module-icon:hover {
    box-shadow: 0 4px 14px rgba(23,48,77,0.10) !important;
    transform: translateY(-1px);
    text-decoration: none !important;
}

/* The icon square inside the tile */
.module-icons-container .module-icon .app-icon,
.modules-container .module-icon .app-icon,
a.module-icon .app-icon,
.module-icon .module-image,
.module-icon > img:first-child {
    width: 40px !important;
    height: 40px !important;
    border-radius: 10px !important;
    margin: 0 0 12px 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #378ADD !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    overflow: hidden;
    flex-shrink: 0;
}
.module-icon .app-icon svg,
.module-icon .app-icon img,
.module-icon > img:first-child {
    width: 24px !important;
    height: 24px !important;
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

/* Tile title (module name) */
.module-icons-container .module-icon .module-title,
.modules-container .module-icon .module-title,
.module-icon .module-title,
a.module-icon > span:not(.app-icon),
a.module-icon > .module-name {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #17304D !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.3 !important;
    text-align: left !important;
    background: transparent !important;
    white-space: normal;
    word-break: break-word;
}

/* Category tint via data-color-set attribute injected by JS
   (we tag each module with a category class after render) */
.module-icon.pt-cat-finance    .app-icon { background-color: #378ADD !important; }
.module-icon.pt-cat-operations .app-icon { background-color: #0F6E56 !important; }
.module-icon.pt-cat-people     .app-icon { background-color: #7F77DD !important; }
.module-icon.pt-cat-configure  .app-icon { background-color: #5F5E5A !important; }

/* Dark mode tiles */
:root[data-theme="dark"] .module-icons-container .module-icon,
:root[data-theme="dark"] .modules-container .module-icon,
:root[data-theme="dark"] a.module-icon {
    background: linear-gradient(110deg, #1A2436 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #1A2436 90%, #253753 70%) !important;
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .module-icon .module-title,
:root[data-theme="dark"] a.module-icon > span:not(.app-icon) {
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .module-icon .app-icon {
    box-shadow: 0 2px 6px rgba(0,0,0,0.35);
}

/* Responsive */
@media (max-width: 768px) {
    .desk-page .module-body,
    .layout-main-section .module-icons-container,
    .container .modules-container {
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important;
        gap: 10px !important;
    }
    .module-icons-container .module-icon,
    a.module-icon {
        padding: 14px 14px !important;
        min-height: 88px !important;
    }
    .module-icon .app-icon { width: 34px !important; height: 34px !important; margin-bottom: 8px !important; }
    .module-icon .app-icon svg, .module-icon .app-icon img { width: 20px !important; height: 20px !important; }
    .module-icon .module-title { font-size: 12.5px !important; }
    .pt-desk-hero { padding: 14px 16px; margin-bottom: 16px; }
    .pt-desk-hero-greeting { font-size: 14.5px; }
    .pt-desk-hero-sub { font-size: 11.5px; }
}
""" + DESK15_END + "\n"


# JS injection: greeting + category tagging.
# It reads existing text (no data mutation), no Frappe API changes.
DESK15_JS_BEGIN = "// === PT-PATCH-15-DESK-HOME BEGIN ==="
DESK15_JS_END   = "// === PT-PATCH-15-DESK-HOME END ==="
DESK15_JS_BLOCK = DESK15_JS_BEGIN + """
(function () {
    // Categorization by module name keywords.
    // Extend by adding more keywords — this is display-only.
    var CATEGORIES = [
        { cls: 'pt-cat-finance',    keys: ['account','buying','selling','asset','financ','tax','payment','invoic'] },
        { cls: 'pt-cat-operations', keys: ['stock','manufactur','project','qualit','subcontract','maintenance','pos','fuel'] },
        { cls: 'pt-cat-people',     keys: ['hr','human','payroll','employee','attendance','leave','shift'] },
        { cls: 'pt-cat-configure',  keys: ['setting','organization','framework','integration','build','portal','showroom','system'] },
    ];

    function categorize(name) {
        var lc = (name || '').toLowerCase();
        for (var i = 0; i < CATEGORIES.length; i++) {
            for (var j = 0; j < CATEGORIES[i].keys.length; j++) {
                if (lc.indexOf(CATEGORIES[i].keys[j]) !== -1) return CATEGORIES[i].cls;
            }
        }
        return 'pt-cat-finance'; // safe default
    }

    function getGreeting() {
        var h = new Date().getHours();
        if (h < 12) return 'Good morning';
        if (h < 18) return 'Good afternoon';
        return 'Good evening';
    }

    function getUserName() {
        try {
            if (window.frappe && frappe.session) {
                return frappe.session.user_fullname
                    || frappe.session.user
                    || 'there';
            }
        } catch (e) {}
        return 'there';
    }

    function getCompanyName() {
        try {
            if (window.frappe && frappe.defaults) {
                var c = frappe.defaults.get_default('company');
                if (c) return c;
            }
        } catch (e) {}
        return '';
    }

    function formatDate() {
        try {
            return new Date().toLocaleDateString(undefined, {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        } catch (e) { return ''; }
    }

    function injectHero(container) {
        if (!container || container.querySelector('.pt-desk-hero')) return;
        var hero = document.createElement('div');
        hero.className = 'pt-desk-hero';
        var company = getCompanyName();
        var date = formatDate();
        var sub = [company, date].filter(Boolean).join(' · ');
        hero.innerHTML =
            '<div class="pt-desk-hero-left">' +
                '<div class="pt-desk-hero-greeting">' + getGreeting() + ', ' + getUserName() + '</div>' +
                '<div class="pt-desk-hero-sub">' + sub + '</div>' +
            '</div>' +
            '<div class="pt-desk-hero-actions">' +
                '<button class="btn btn-primary btn-sm" onclick="frappe.new_doc && frappe.route_options={} , frappe.set_route(\\'newdoc\\')">+ New</button>' +
                '<button class="btn btn-default btn-sm" onclick="frappe.searchdialog && frappe.searchdialog.search.show()">Search</button>' +
            '</div>';
        container.insertBefore(hero, container.firstChild);
    }

    function tagModuleTiles() {
        var tiles = document.querySelectorAll('.module-icon, a.module-icon');
        tiles.forEach(function (tile) {
            if (tile.dataset.ptCatDone) return;
            var name = (tile.querySelector('.module-title, .module-name') || {}).textContent
                    || tile.getAttribute('title')
                    || tile.textContent;
            var cls = categorize(name);
            tile.classList.add(cls);
            tile.dataset.ptCatDone = '1';
        });
    }

    function findDeskHomeContainer() {
        // Frappe /app root — the modules grid lives inside one of these
        return document.querySelector('.module-icons-container')
            || document.querySelector('.modules-container')
            || document.querySelector('.desk-page .layout-main-section');
    }

    function refresh() {
        try {
            tagModuleTiles();
            var container = findDeskHomeContainer();
            if (container) {
                // Only inject hero on the actual home route
                var path = (window.location.hash || window.location.pathname || '').toLowerCase();
                var isHome = /\/app\/?$|\/app\/home|\/app\/build/.test(path) || path === '' || path === '/app';
                if (isHome && container.parentNode) {
                    injectHero(container.parentNode);
                }
            }
        } catch (e) { /* silent — never break the desk */ }
    }

    if (document.readyState !== 'loading') refresh();
    else document.addEventListener('DOMContentLoaded', refresh);
    window.addEventListener('load', refresh);

    // Re-run on route change (Frappe uses hash-based routing on the desk)
    window.addEventListener('hashchange', function () { setTimeout(refresh, 200); });
    window.addEventListener('popstate',   function () { setTimeout(refresh, 200); });

    // Fallback for late-rendered tiles
    setTimeout(refresh, 800);
    setTimeout(refresh, 2500);
})();
""" + DESK15_JS_END + "\n"


def _inject_desk15_js():
    if not os.path.exists(PORTAL_JS_PATH):
        print(f">>> WARN: {PORTAL_JS_PATH} not found; skipping desk-home JS"); return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    current = re.sub(
        re.escape(DESK15_JS_BEGIN) + r".*?" + re.escape(DESK15_JS_END) + r"\n?",
        "", current, flags=re.DOTALL,
    )
    with open(PORTAL_JS_PATH, "w") as f:
        f.write(current.rstrip() + "\n\n" + DESK15_JS_BLOCK)
    print(f"[js] injected desk-home block into {PORTAL_JS_PATH}")


def _strip_desk15_js():
    if not os.path.exists(PORTAL_JS_PATH): return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    new = re.sub(
        re.escape(DESK15_JS_BEGIN) + r".*?" + re.escape(DESK15_JS_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    with open(PORTAL_JS_PATH, "w") as f: f.write(new)
    print("[js] desk-home block stripped")


def apply_15_desk_home():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_15_desk_home")
    _ensure_original_file(PORTAL_JS_PATH, "portal_theme.js")
    _timestamp_backup_file(PORTAL_JS_PATH, "before_15_portal_theme.js")

    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    current = re.sub(
        re.escape(DESK15_BEGIN) + r".*?" + re.escape(DESK15_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + DESK15_CSS
    _save_css(new_css)

    _inject_desk15_js()

    frappe.db.commit(); frappe.clear_cache()
    print("")
    print("[done] Patch 15 applied — desk home restyled.")
    print("       Hard-refresh /app (Ctrl+Shift+R).")


def rollback_15_desk_home():
    _timestamp_backup_css("before_ROLLBACK_15_desk_home")
    _timestamp_backup_file(PORTAL_JS_PATH, "before_ROLLBACK_15_portal_theme.js")

    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(DESK15_BEGIN) + r".*?" + re.escape(DESK15_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)

    _strip_desk15_js()

    frappe.db.commit(); frappe.clear_cache()
    print("[done] Patch 15 rolled back.")


# =====================================================
# PATCH 15v2 — Desk home: correct v16 selectors
# =====================================================
DESK15V2_BEGIN = "/* PT-PATCH:15v2-desk-home BEGIN */"
DESK15V2_END   = "/* PT-PATCH:15v2-desk-home END */"

DESK15V2_CSS = DESK15V2_BEGIN + """
/* Grid container */
.icons {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
    gap: 14px !important;
    padding: 8px 0 !important;
    align-items: stretch !important;
}

/* Each tile — gradient card */
.desktop-icon {
    background: linear-gradient(110deg, #eceef3 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #eceef3 90%, #d4e1f0 70%) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    border: 0 !important;
    box-shadow: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    text-decoration: none !important;
    min-height: 108px !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
    color: #17304D !important;
}
.desktop-icon:hover {
    box-shadow: 0 4px 14px rgba(23,48,77,0.10) !important;
    transform: translateY(-1px);
    text-decoration: none !important;
}

/* Icon container inside tile */
.desktop-icon .icon-container {
    margin: 0 0 12px 0 !important;
    padding: 0 !important;
    display: block !important;
    text-align: left !important;
}
.desktop-icon .app-icon {
    width: 44px !important;
    height: 44px !important;
    border-radius: 10px !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    overflow: hidden;
    flex-shrink: 0;
}
.desktop-icon .app-icon .inner,
.desktop-icon .app-icon svg,
.desktop-icon .app-icon i {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 1 !important;
}

/* Tile label */
.desktop-icon .module-title,
.desktop-icon .app-title,
.desktop-icon > span:not(.icon-container):not(.app-icon),
.desktop-icon .desktop-icon-label {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #17304D !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.3 !important;
    text-align: left !important;
    background: transparent !important;
    white-space: normal;
    word-break: break-word;
}

/* Dark mode */
:root[data-theme="dark"] .desktop-icon {
    background: linear-gradient(110deg, #1A2436 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #1A2436 90%, #253753 70%) !important;
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .desktop-icon .module-title,
:root[data-theme="dark"] .desktop-icon > span:not(.icon-container):not(.app-icon) {
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .desktop-icon .app-icon {
    box-shadow: 0 2px 6px rgba(0,0,0,0.35);
}

/* Responsive */
@media (max-width: 768px) {
    .icons {
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important;
        gap: 10px !important;
    }
    .desktop-icon { padding: 14px !important; min-height: 92px !important; }
    .desktop-icon .app-icon { width: 36px !important; height: 36px !important; margin-bottom: 8px !important; }
    .desktop-icon .app-icon .inner { font-size: 17px !important; }
    .desktop-icon .module-title { font-size: 12.5px !important; }
}
""" + DESK15V2_END + "\n"


def apply_15v2_desk_home():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_15v2_desk_home")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Strip any prior 15 or 15v2 blocks
    current = re.sub(
        r"/\* PT-PATCH:15-desk-home BEGIN \*/.*?/\* PT-PATCH:15-desk-home END \*/\n?",
        "", current, flags=re.DOTALL,
    )
    current = re.sub(
        re.escape(DESK15V2_BEGIN) + r".*?" + re.escape(DESK15V2_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + DESK15V2_CSS
    _save_css(new_css)
    print("[done] Patch 15v2 applied. Hard-refresh /app (Ctrl+Shift+R).")


def rollback_15v2_desk_home():
    _timestamp_backup_css("before_ROLLBACK_15v2_desk_home")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(DESK15V2_BEGIN) + r".*?" + re.escape(DESK15V2_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 15v2 rolled back.")


# =====================================================
# PATCH 15v3 — Fix grid collapse (flex override + item sizing)
# =====================================================
DESK15V3_BEGIN = "/* PT-PATCH:15v3-desk-home BEGIN */"
DESK15V3_END   = "/* PT-PATCH:15v3-desk-home END */"

DESK15V3_CSS = DESK15V3_BEGIN + """
/* Container — use flex-wrap (matches Frappe's own flex layout) instead
   of grid, so it works even if Frappe injects inline flex styles. */
.icons {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 14px !important;
    padding: 12px 0 !important;
    align-items: stretch !important;
    justify-content: flex-start !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* Each tile — fixed flex-basis so multiple sit per row */
.icons .desktop-icon,
.desktop-icon {
    background: linear-gradient(110deg, #eceef3 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #eceef3 90%, #d4e1f0 70%) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    border: 0 !important;
    box-shadow: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    text-decoration: none !important;
    color: #17304D !important;

    /* Sizing: fixed width so ~5-6 per row on wide screens */
    flex: 0 0 calc(16.6% - 12px) !important;
    max-width: calc(16.6% - 12px) !important;
    min-width: 150px !important;
    min-height: 108px !important;
    box-sizing: border-box !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.icons .desktop-icon:hover,
.desktop-icon:hover {
    box-shadow: 0 4px 14px rgba(23,48,77,0.10) !important;
    transform: translateY(-1px);
    text-decoration: none !important;
}

/* Icon square inside tile */
.desktop-icon .icon-container {
    margin: 0 0 12px 0 !important;
    padding: 0 !important;
    display: block !important;
    text-align: left !important;
    width: auto !important;
    height: auto !important;
}
.desktop-icon .app-icon {
    width: 44px !important;
    height: 44px !important;
    border-radius: 10px !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    overflow: hidden;
    flex-shrink: 0;
}
.desktop-icon .app-icon .inner,
.desktop-icon .app-icon svg,
.desktop-icon .app-icon i {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 1 !important;
}

/* Tile label */
.desktop-icon .module-title,
.desktop-icon .app-title,
.desktop-icon > span:not(.icon-container):not(.app-icon),
.desktop-icon .desktop-icon-label {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #17304D !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.3 !important;
    text-align: left !important;
    background: transparent !important;
    white-space: normal;
    word-break: break-word;
}

/* Dark mode */
:root[data-theme="dark"] .icons .desktop-icon,
:root[data-theme="dark"] .desktop-icon {
    background: linear-gradient(110deg, #1A2436 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #1A2436 90%, #253753 70%) !important;
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .desktop-icon .module-title,
:root[data-theme="dark"] .desktop-icon > span:not(.icon-container):not(.app-icon) {
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .desktop-icon .app-icon {
    box-shadow: 0 2px 6px rgba(0,0,0,0.35);
}

/* Responsive columns via percentage flex-basis */
@media (max-width: 1400px) {
    .icons .desktop-icon, .desktop-icon {
        flex: 0 0 calc(20% - 12px) !important;
        max-width: calc(20% - 12px) !important;
    }
}
@media (max-width: 1100px) {
    .icons .desktop-icon, .desktop-icon {
        flex: 0 0 calc(25% - 12px) !important;
        max-width: calc(25% - 12px) !important;
    }
}
@media (max-width: 900px) {
    .icons .desktop-icon, .desktop-icon {
        flex: 0 0 calc(33.33% - 12px) !important;
        max-width: calc(33.33% - 12px) !important;
    }
}
@media (max-width: 700px) {
    .icons .desktop-icon, .desktop-icon {
        flex: 0 0 calc(50% - 8px) !important;
        max-width: calc(50% - 8px) !important;
        padding: 14px !important;
        min-height: 92px !important;
    }
    .desktop-icon .app-icon { width: 36px !important; height: 36px !important; margin-bottom: 8px !important; }
    .desktop-icon .app-icon .inner { font-size: 17px !important; }
    .desktop-icon .module-title { font-size: 12.5px !important; }
    .icons { gap: 10px !important; }
}
@media (max-width: 480px) {
    .icons .desktop-icon, .desktop-icon {
        flex: 0 0 100% !important;
        max-width: 100% !important;
    }
}
""" + DESK15V3_END + "\n"


def apply_15v3_desk_home():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_15v3_desk_home")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Strip any prior 15, 15v2, 15v3 blocks
    current = re.sub(
        r"/\* PT-PATCH:15-desk-home BEGIN \*/.*?/\* PT-PATCH:15-desk-home END \*/\n?",
        "", current, flags=re.DOTALL,
    )
    current = re.sub(
        r"/\* PT-PATCH:15v2-desk-home BEGIN \*/.*?/\* PT-PATCH:15v2-desk-home END \*/\n?",
        "", current, flags=re.DOTALL,
    )
    current = re.sub(
        re.escape(DESK15V3_BEGIN) + r".*?" + re.escape(DESK15V3_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()
    new_css = current + "\n\n" + DESK15V3_CSS
    _save_css(new_css)
    print("[done] Patch 15v3 applied. Hard-refresh /app (Ctrl+Shift+R).")


def rollback_15v3_desk_home():
    _timestamp_backup_css("before_ROLLBACK_15v3_desk_home")
    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(DESK15V3_BEGIN) + r".*?" + re.escape(DESK15V3_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    print("[done] Patch 15v3 rolled back.")


# =====================================================
# PATCH 15v4 — Final desk home: correct DOM (icon-container + icon-caption)
# =====================================================
DESK15V4_BEGIN = "/* PT-PATCH:15v4-desk-home BEGIN */"
DESK15V4_END   = "/* PT-PATCH:15v4-desk-home END */"

DESK15V4_CSS = DESK15V4_BEGIN + """
/* ============ HERO BAND (injected by JS) ============ */
.pt-desk-hero {
    background: #FFFFFF;
    border: 1px solid #E1E7EE;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 12px 0 24px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
}
.pt-desk-hero-left { min-width: 0; flex: 1; }
.pt-desk-hero-greeting {
    font-size: 16px;
    font-weight: 600;
    color: #17304D;
    margin: 0 0 4px;
    line-height: 1.3;
}
.pt-desk-hero-sub {
    font-size: 12.5px;
    color: #5A6B80;
    margin: 0;
}
.pt-desk-hero-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.pt-desk-hero-actions .btn {
    border-radius: 999px !important;
    padding: 6px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: auto !important;
}
:root[data-theme="dark"] .pt-desk-hero { background: #1A2436; border-color: #2A3548; }
:root[data-theme="dark"] .pt-desk-hero-greeting { color: #E6EAF0; }
:root[data-theme="dark"] .pt-desk-hero-sub { color: #A0AAB6; }

/* ============ MODULES section label (injected by JS) ============ */
.pt-modules-label {
    font-size: 11px;
    font-weight: 700;
    color: #5A6B80;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 4px 0 12px 4px;
}
:root[data-theme="dark"] .pt-modules-label { color: #A0AAB6; }

/* ============ TILE GRID ============ */
/* Override Frappe's inline "display: grid" so we control spacing */
.icons-container .icons,
.icons {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)) !important;
    gap: 14px !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}

/* ============ EACH TILE (a.desktop-icon) ============ */
.desktop-icon {
    background: linear-gradient(110deg, #eceef3 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #eceef3 90%, #d4e1f0 70%) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    border: 0 !important;
    box-shadow: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    text-decoration: none !important;
    min-height: 118px !important;
    color: #17304D !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
    box-sizing: border-box !important;
    width: auto !important;
    max-width: none !important;
    flex: none !important;
}
.desktop-icon:hover {
    box-shadow: 0 4px 14px rgba(23,48,77,0.10) !important;
    transform: translateY(-1px);
    text-decoration: none !important;
}

/* Icon square wrapper — kept small, top-left */
.desktop-icon .icon-container {
    width: 44px !important;
    height: 44px !important;
    margin: 0 0 12px 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* Frappe's icon <img> — keep its own colors, just size it */
.desktop-icon .icon-container .app-icon,
.desktop-icon .app-icon {
    width: 44px !important;
    height: 44px !important;
    max-width: 44px !important;
    max-height: 44px !important;
    border-radius: 10px !important;
    object-fit: contain !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    display: block !important;
}

/* Caption/title area */
.desktop-icon .icon-caption {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
    display: block !important;
}
.desktop-icon .icon-caption .icon-title,
.desktop-icon .icon-title {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #17304D !important;
    margin: 0 0 4px 0 !important;
    padding: 0 !important;
    line-height: 1.3 !important;
    text-align: left !important;
    background: transparent !important;
    white-space: normal;
    word-break: break-word;
}

/* Subtitle inside caption (rendered by JS from data-id) */
.desktop-icon .icon-caption .icon-subtitle,
.desktop-icon .icon-subtitle {
    font-size: 11.5px !important;
    font-weight: 400 !important;
    color: #5A6B80 !important;
    line-height: 1.3 !important;
    margin: 0 !important;
    text-align: left !important;
}

/* Dark mode */
:root[data-theme="dark"] .desktop-icon {
    background: linear-gradient(110deg, #1A2436 40%, transparent 30%),
                radial-gradient(farthest-corner at 0% 0%, #1A2436 90%, #253753 70%) !important;
    color: #E6EAF0 !important;
}
:root[data-theme="dark"] .desktop-icon .icon-title { color: #E6EAF0 !important; }
:root[data-theme="dark"] .desktop-icon .icon-subtitle { color: #A0AAB6 !important; }

/* Responsive */
@media (max-width: 768px) {
    .icons-container .icons, .icons {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)) !important;
        gap: 10px !important;
    }
    .desktop-icon { padding: 16px !important; min-height: 100px !important; }
    .desktop-icon .icon-container, .desktop-icon .app-icon { width: 36px !important; height: 36px !important; }
    .desktop-icon .icon-title { font-size: 13px !important; }
    .desktop-icon .icon-subtitle { font-size: 11px !important; }
    .pt-desk-hero { padding: 14px 16px; margin-bottom: 18px; }
    .pt-desk-hero-greeting { font-size: 14.5px; }
    .pt-desk-hero-sub { font-size: 11.5px; }
}
""" + DESK15V4_END + "\n"


DESK15V4_JS_BEGIN = "// === PT-PATCH-15V4-DESK-HOME BEGIN ==="
DESK15V4_JS_END   = "// === PT-PATCH-15V4-DESK-HOME END ==="
DESK15V4_JS_BLOCK = DESK15V4_JS_BEGIN + """
(function () {
    // Subtitle keywords -> short human descriptors.
    // Add more entries here to customize any module label.
    var SUBTITLES = {
        'framework': 'System & custom',
        'fuel station': 'Fuel tracking',
        'organization': 'Companies & users',
        'accounting': 'Ledger & reports',
        'assets': 'Fixed assets',
        'buying': 'Suppliers & POs',
        'manufacturing': 'BOM & work orders',
        'pos system': 'Point of sale',
        'projects': 'Tasks & timesheets',
        'quality': 'Inspections',
        'selling': 'Customers & SOs',
        'stock': 'Items & warehouses',
        'subcontracting': 'Vendor work',
        'dagaarsoft settings': 'Portal theme',
        'framework hr': 'HR & payroll',
        'showrooms': 'Retail outlets'
    };

    function getGreeting() {
        var h = new Date().getHours();
        if (h < 12) return 'Good morning';
        if (h < 18) return 'Good afternoon';
        return 'Good evening';
    }

    function getUserName() {
        try {
            if (window.frappe && frappe.session) {
                return frappe.session.user_fullname || frappe.session.user || 'there';
            }
        } catch (e) {}
        return 'there';
    }

    function getCompanyName() {
        try {
            if (window.frappe && frappe.defaults) {
                var c = frappe.defaults.get_default('company');
                if (c) return c;
            }
        } catch (e) {}
        return '';
    }

    function formatDate() {
        try {
            return new Date().toLocaleDateString(undefined, {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        } catch (e) { return ''; }
    }

    function injectHero() {
        if (document.querySelector('.pt-desk-hero')) return;
        var grid = document.querySelector('.icons-container') || document.querySelector('.icons');
        if (!grid || !grid.parentNode) return;

        var hero = document.createElement('div');
        hero.className = 'pt-desk-hero';
        var company = getCompanyName();
        var date = formatDate();
        var sub = [company, date].filter(Boolean).join(' \u00b7 ');
        hero.innerHTML =
            '<div class="pt-desk-hero-left">' +
                '<div class="pt-desk-hero-greeting">' + getGreeting() + ', ' + getUserName() + '</div>' +
                '<div class="pt-desk-hero-sub">' + sub + '</div>' +
            '</div>' +
            '<div class="pt-desk-hero-actions">' +
                '<button class="btn btn-primary btn-sm pt-hero-new">+ New</button>' +
                '<button class="btn btn-default btn-sm pt-hero-search">Search</button>' +
            '</div>';
        grid.parentNode.insertBefore(hero, grid);

        // Modules label
        if (!document.querySelector('.pt-modules-label')) {
            var label = document.createElement('div');
            label.className = 'pt-modules-label';
            label.textContent = 'Modules';
            grid.parentNode.insertBefore(label, grid);
        }

        // Wire buttons
        var newBtn = hero.querySelector('.pt-hero-new');
        if (newBtn) newBtn.addEventListener('click', function () {
            try { frappe.set_route('newdoc'); } catch (e) {}
        });
        var searchBtn = hero.querySelector('.pt-hero-search');
        if (searchBtn) searchBtn.addEventListener('click', function () {
            try {
                if (frappe.searchdialog && frappe.searchdialog.search) {
                    frappe.searchdialog.search.show();
                } else {
                    var awesomeBar = document.querySelector('#navbar-search, .search-bar input');
                    if (awesomeBar) awesomeBar.focus();
                }
            } catch (e) {}
        });
    }

    function addSubtitles() {
        var tiles = document.querySelectorAll('.desktop-icon');
        tiles.forEach(function (tile) {
            if (tile.dataset.ptSubtitleDone) return;
            var caption = tile.querySelector('.icon-caption');
            if (!caption) return;
            if (caption.querySelector('.icon-subtitle')) { tile.dataset.ptSubtitleDone = '1'; return; }

            var name = (tile.getAttribute('data-id') || '').toLowerCase().trim();
            var sub = SUBTITLES[name] || '';
            if (!sub) { tile.dataset.ptSubtitleDone = '1'; return; }

            var subEl = document.createElement('div');
            subEl.className = 'icon-subtitle';
            subEl.textContent = sub;
            caption.appendChild(subEl);
            tile.dataset.ptSubtitleDone = '1';
        });
    }

    function refresh() {
        try {
            addSubtitles();
            var path = (window.location.hash || window.location.pathname || '').toLowerCase();
            var isHome = /\\/app\\/?$|\\/app\\/home|\\/app\\/build|\\/app\\/apps/.test(path)
                        || path === '' || path === '/app' || path === '/app/';
            if (isHome) injectHero();
        } catch (e) { /* never break desk */ }
    }

    if (document.readyState !== 'loading') refresh();
    else document.addEventListener('DOMContentLoaded', refresh);
    window.addEventListener('load', refresh);
    window.addEventListener('hashchange', function () { setTimeout(refresh, 200); });
    window.addEventListener('popstate',   function () { setTimeout(refresh, 200); });
    setTimeout(refresh, 800);
    setTimeout(refresh, 2500);
})();
""" + DESK15V4_JS_END + "\n"


def _inject_desk15v4_js():
    if not os.path.exists(PORTAL_JS_PATH): return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    # Strip any prior desk-home JS variants
    current = re.sub(re.escape("// === PT-PATCH-15-DESK-HOME BEGIN ===")+r".*?"+re.escape("// === PT-PATCH-15-DESK-HOME END ===")+r"\n?", "", current, flags=re.DOTALL)
    current = re.sub(re.escape(DESK15V4_JS_BEGIN)+r".*?"+re.escape(DESK15V4_JS_END)+r"\n?", "", current, flags=re.DOTALL)
    with open(PORTAL_JS_PATH, "w") as f:
        f.write(current.rstrip() + "\n\n" + DESK15V4_JS_BLOCK)
    print(f"[js] desk-home v4 injected into {PORTAL_JS_PATH}")


def _strip_desk15v4_js():
    if not os.path.exists(PORTAL_JS_PATH): return
    with open(PORTAL_JS_PATH, "r") as f: current = f.read()
    new = re.sub(re.escape(DESK15V4_JS_BEGIN)+r".*?"+re.escape(DESK15V4_JS_END)+r"\n?", "", current, flags=re.DOTALL).rstrip()+"\n"
    with open(PORTAL_JS_PATH, "w") as f: f.write(new)


def apply_15v4_desk_home():
    if not frappe.db.exists("Theme Template", TEMPLATE):
        print(f">>> ERROR: Theme Template '{TEMPLATE}' not found."); return
    _timestamp_backup_css("before_15v4_desk_home")
    _timestamp_backup_file(PORTAL_JS_PATH, "before_15v4_portal_theme.js")

    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    # Strip all previous 15* CSS blocks
    for tag in ["15-desk-home", "15v2-desk-home", "15v3-desk-home"]:
        current = re.sub(
            r"/\* PT-PATCH:" + tag + r" BEGIN \*/.*?/\* PT-PATCH:" + tag + r" END \*/\n?",
            "", current, flags=re.DOTALL,
        )
    current = re.sub(
        re.escape(DESK15V4_BEGIN) + r".*?" + re.escape(DESK15V4_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip()

    new_css = current + "\n\n" + DESK15V4_CSS
    _save_css(new_css)
    _inject_desk15v4_js()

    frappe.db.commit(); frappe.clear_cache()
    print("[done] Patch 15v4 applied. Hard-refresh /app (Ctrl+Shift+R).")


def rollback_15v4_desk_home():
    _timestamp_backup_css("before_ROLLBACK_15v4_desk_home")
    _timestamp_backup_file(PORTAL_JS_PATH, "before_ROLLBACK_15v4_portal_theme.js")

    current = frappe.db.get_value("Theme Template", TEMPLATE, "theme_template") or ""
    new_css = re.sub(
        re.escape(DESK15V4_BEGIN) + r".*?" + re.escape(DESK15V4_END) + r"\n?",
        "", current, flags=re.DOTALL,
    ).rstrip() + "\n"
    _save_css(new_css)
    _strip_desk15v4_js()

    frappe.db.commit(); frappe.clear_cache()
    print("[done] Patch 15v4 rolled back.")
