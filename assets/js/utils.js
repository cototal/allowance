import $ from "jquery";

export function isEmpty(thing) {
    if (thing == null) {
        return true;
    }

    if ((typeof thing === "string" || Array.isArray(thing)) && thing.length === 0) {
        return true;
    }

    if (typeof thing === "object" && Object.keys(thing).length === 0) {
        return true;
    }

    return false;
}

export function ajaxLinkHandler(evt) {
    evt.preventDefault();
    const target = evt.target;
    let data = {};
    for (let attr of ["href", "data-return-to", "data-method", "data-confirm"]) {
        data[attr.replace("data-", "")] = target.getAttribute(attr);
    }
    if (isEmpty(data["confirm"])) {
        data["confirm"] = "Are you sure?";
    }
    if (!confirm(data["confirm"])) {
        return;
    }

    $.ajax(data["href"], {
        method: data["method"]
    }).then(() => {
        if (!isEmpty(data["return-to"])) {
            window.location.href = data["return-to"];
        }
    }).catch(err => {
        console.error(err);
    });
}