/** @odoo-module **/

import {registry} from "@web/core/registry";
import {user_menuitems} from "@web/webclient/user_menu/user_menu_items";

if (registry.category("user_menuitems")) {
    registry.category("user_menuitems").remove("documentation");
    registry.category("user_menuitems").remove("support");
    registry.category("user_menuitems").remove("odoo_account");
}
