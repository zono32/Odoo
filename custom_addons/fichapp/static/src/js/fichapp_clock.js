/** @odoo-module **/
import { registry } from "@web/core/registry";
const { useEffect, useRef } = owl;

// Este script buscará los elementos del reloj y los actualizará cada segundo
setInterval(() => {
    const clockEl = document.getElementById('fichapp_clock');
    const dateEl = document.getElementById('fichapp_date');
    
    if (clockEl || dateEl) {
        const now = new Date();
        
        if (clockEl) {
            clockEl.innerText = now.toLocaleTimeString('es-ES', { 
                hour: '2-digit', minute: '2-digit', second: '2-digit' 
            });
        }
        
        if (dateEl) {
            const options = { weekday: 'long', day: 'numeric', month: 'long' };
            dateEl.innerText = now.toLocaleDateString('es-ES', options);
        }
    }
}, 1000);
