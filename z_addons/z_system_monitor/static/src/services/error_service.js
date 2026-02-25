/** @odoo-module **/
import {
    ConnectionLostError,
    RPCError
} from "@web/core/network/rpc_service";
import {
    registry
} from "@web/core/registry";

export function LogErrorService(env, error, originalError) {
    const rpcError = error instanceof RPCError ? error : (originalError instanceof RPCError ? originalError : null);
    if (rpcError) {
        const params = {
            name: error.message,
            type: "client",
            level: "error",
            path: window.location.href,
            func: rpcError.data.debug,
            message: rpcError.data.message,
            line: 1,
        };
        try {
            env.services.orm.create("ir.logging", [params]);
        } catch (e) {
            console.error("Failed to log error:", e);
        }
    }
}

registry.category("error_handlers").add("LogErrorService", LogErrorService, {
    sequence: 96
});