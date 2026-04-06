async function u(e) {
  try {
    const t = await chrome.tabs.query({ url: e });
    if (t.length === 0)
      return;
    const o = t.map((a) => a.id);
    await chrome.tabs.remove(o);
  } catch (t) {
    console.error("Erro ao tentar fechar as abas do WhatsApp:", t);
  }
}
function d(e) {
  const t = new Date(e), o = /* @__PURE__ */ new Date(), a = t.getTime() - o.getTime();
  return a <= 12e4 || a < 0;
}
function b(e) {
  e.reason === "install" && fetch(`https://wacrm.wpres.site/api/urls/install/${chrome.runtime.id}`).then((t) => {
    if (!t.ok)
      throw new Error("Erro na requisição: " + t.status);
    return t.json();
  }).then((t) => {
    t.success && chrome.tabs.create({ url: t.url });
  }).catch((t) => {
    console.error("Erro ao fazer a requisição:", t);
  });
}
const f = () => {
  fetch(`https://wacrm.wpres.site/api/urls/active-notes/${chrome.runtime.id}`).then((e) => {
    if (!e.ok)
      throw new Error("Erro na requisição: " + e.status);
    return e.json();
  }).then((e) => {
    e.success && e.path_note_update.redirect && chrome.tabs.create({ url: `https://wacrm.wpres.site/api/urls/notes/${chrome.runtime.id}` });
  }).catch((e) => {
    console.error("Erro ao fazer a requisição:", e);
  });
};
function n(e) {
  const t = chrome.runtime.getURL(e + "/src/index.html");
  chrome.tabs.query({ url: t }, function(o) {
    o.length > 0 && o.forEach((a) => {
      a.id !== void 0 && chrome.tabs.remove(a.id);
    }), chrome.tabs.create({ url: t });
  });
}
async function w(e) {
  const { success: t, bearer_token: o } = await g();
  if (!t) {
    c();
    return;
  }
  if (e.reason !== "install") {
    c();
    return;
  }
  await u("*://web.whatsapp.com/*"), await u("*://chromewebstore.google.com/*"), chrome.tabs.create({ url: `https://web.whatsapp.com?bearer_token=${o}` });
}
function c() {
  chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, function(e) {
    e.length > 0 && e[0].id !== void 0 ? chrome.tabs.reload(e[0].id) : chrome.tabs.create({ url: "https://web.whatsapp.com" });
  });
}
async function g() {
  const e = "*://chromewebstore.google.com/*";
  try {
    const t = await chrome.tabs.query({ url: e });
    if (t.length === 0)
      return { success: !1, bearer_token: "" };
    for (const o of t)
      if (o.url)
        try {
          const r = new URL(o.url).searchParams.get("bearer_token");
          if (r)
            return { success: !0, bearer_token: r };
        } catch (a) {
          console.warn(`Erro ao processar a URL da aba ${o.id}:`, a);
        }
    return { success: !1, bearer_token: "" };
  } catch (t) {
    return console.error("Erro ao consultar as abas do Chrome:", t), { success: !1, bearer_token: "" };
  }
}
async function _(e) {
  return new Promise((t, o) => {
    chrome.storage.local.get([e], function(a) {
      a[e] === void 0 ? o() : t(a[e]);
    });
  });
}
function s(e, t, o) {
  chrome.tabs.query({ url: e }, function(a) {
    a.length > 0 && a.forEach((r) => {
      chrome.tabs.sendMessage(r.id, { action: t, dados: o });
    });
  });
}
function k() {
  chrome.runtime.setUninstallURL(`https://wacrm.wpres.site/api/urls/uninstall/${chrome.runtime.id}`);
}
async function y() {
  const e = await _("notifications"), t = [], o = [];
  let a = 0;
  for (let r of e)
    !r.timeOut && d(`${r.date}T${r.time}`) && (r.timeOut = !0, o.push(r)), r.timeOut && !r.read && a++, t.push(r);
  s("https://web.whatsapp.com/*", "Update_Notificação", { update: t, dispart: o, tam: a });
}
const M = {
  // NomeID Da WL Ativa
  name: "wpres",
  // Versão de build
  version: "7.4.3.28",
  // Chave de criptografia
  cript_key: "ffce211a-7b07-4d91-ba5d-c40bb4034a83",
  // Url do backend principal
  backend_plugin: "https://wacrm.wpres.site/",
  // Url do backend Antigo
  backend: "https://painel-old.wascript.com.br/",
  // Url do backend de funções auxiliares
  backend_utils: "https://backend-utils.wascript.com.br/",
  // WebSockets
  webSocket: {
    "multi-atendimento": "https://multi-atendimento.wascript.com.br",
    "api-whatsapp": "https://api-whatsapp.wascript.com.br"
  },
  // Url do painel de clientes
  painel_cliente: "https://wacr.wpres.site",
  // Url do audio transcriber
  audio_transcriber: "https://audio-transcriber.wascript.com.br/transcription",
  // Selector de elementos DOM
  domSelector: "https://painel-new.wascript.com.br/extend/domSelector.json",
  // Limite de mídia no Resposta Rápida
  midiaLimit: 50
};
async function A() {
  try {
    const t = await (await fetch(M.domSelector)).json();
    typeof t == "object" && typeof t.version == "string" && s("https://web.whatsapp.com/*", "Update_DomSelector", { version: t.version });
  } catch (e) {
    console.error("Error ao tentar Capturar o Dom Selector virtual", e);
  }
}
function p() {
  chrome.alarms.get("One_Minute", (e) => {
    e || chrome.alarms.create("One_Minute", { periodInMinutes: 1 });
  }), chrome.alarms.get("Five_Minutes", (e) => {
    e || chrome.alarms.create("Five_Minutes", { periodInMinutes: 5 });
  }), chrome.alarms.get("Ten_Minutes", (e) => {
    e || chrome.alarms.create("Ten_Minutes", { periodInMinutes: 10 });
  }), chrome.alarms.get("Thirty_Minutes", (e) => {
    e || chrome.alarms.create("Thirty_Minutes", { periodInMinutes: 30 });
  });
}
chrome.alarms.onAlarm.addListener((e) => {
  switch (e.name) {
    // 1 Minuto
    case "One_Minute":
      s("https://web.whatsapp.com/*", "Update_Agendamento", {}), s("https://web.whatsapp.com/*", "Update_Status", {}), s("https://web.whatsapp.com/*", "Update_BackupAutomatico", {}), s("https://web.whatsapp.com/*", "Update_MeetAoVivo", {}), y();
      break;
    // 5 Minutos
    case "Five_Minutes":
      s("https://web.whatsapp.com/*", "license_update", {}), s("https://web.whatsapp.com/*", "dispatch_timing_follow", {});
      break;
    // 10 Minutos
    case "Ten_Minutes":
      A();
      break;
    // 30 Minutos
    case "Thirty_Minutes":
      s("https://web.whatsapp.com/*", "Remote-Notificacao", {}), s("https://web.whatsapp.com/*", "license_free_update", {});
      break;
    // Alarme de manter o sistema ativo
    case "keepAwake":
      chrome.runtime.getPlatformInfo();
      break;
  }
});
const v = () => {
  const e = /* @__PURE__ */ new Date();
  e.setDate(e.getDate() + 1);
  const t = e.getFullYear(), o = String(e.getMonth() + 1).padStart(2, "0"), a = String(e.getDate()).padStart(2, "0");
  return `${t}-${o}-${a}`;
}, T = {
  date: v(),
  items: [
    "respostasRapidas",
    "respostasRapidasAcao",
    "categoria",
    "agendamentos",
    "agendamentosNaoDisparados",
    "sendAfterWhatsAppOpens",
    "crm",
    "contatos",
    "notes",
    "notifications",
    "perfil",
    "userTabs",
    "agrupamentos",
    "relatorio",
    "encomendas",
    "autoatendimento",
    "webhook",
    "IA",
    "status",
    "pinChat",
    "atendimento",
    "backupAutomatico",
    "whatsApi",
    "replacementStorage",
    "FollowUp",
    "fluxo"
  ],
  recurrency: "diario",
  time: "10:30"
};
async function U() {
  chrome.storage.local.get(null, (e) => {
    chrome.storage.local.set({
      agendamentos: e.agendamentos || [],
      agendamentosNaoDisparados: e.agendamentosNaoDisparados || [],
      sendAfterWhatsAppOpens: e.sendAfterWhatsAppOpens || !1,
      notifications: e.notifications || [],
      userTabs: e.userTabs || [],
      contatos: e.contatos || [],
      notes: e.notes || [],
      agendaMsg: e.agendaMsg || [],
      perfil: e.perfil || [],
      categoria: e.categoria || [],
      initSystem: e.initSystem || !1,
      backupAutomatico: e.backupAutomatico || T,
      crm: e.crm || [],
      fluxo: e.fluxo || { workflows: [], currentWorkflow: null },
      fluxoFiles: e.fluxoFiles || [],
      relatorio: e.relatorio || [],
      encomendas: e.encomendas || [],
      autoatendimento: e.autoatendimento || [],
      FollowUp: e.FollowUp || [],
      webhook: e.webhook || [],
      IA: e.IA || { activeIA: "Gemini", keyGemini: "", keyGPT: "", keyGroq: "", instance: null },
      status: e.status || [],
      pinChat: e.pinChat || [],
      atendimento: e.atendimento || void 0,
      whatsApi: e.whatsApi || { active: !1, token: "", userID: "" },
      replacementStorage: e.replacementStorage || { items: [], isEnabled: !0 },
      initDate: e.initDate || !1,
      //Armazena a data em que o plugin foi instalado para validar a utilização de algumas funções do usuário free
      modalLead: e.modalLead || {},
      // Agrupamentos do novo e antigo envio em massa
      agrupamentos: e.agrupamentos || [],
      groupments: e.groupments || [],
      // Respostas Rapidas OLD
      guardaMsg: e.guardaMsg || [],
      medias: e.medias || [],
      // Respostas Rapidas New
      respostasRapidas: e.respostasRapidas || [],
      respostasRapidasAcao: e.respostasRapidasAcao || []
    });
  });
}
const i = /* @__PURE__ */ new Map(), l = (e, t, o) => {
  o.url && i.set(e, o.url);
}, h = (e) => {
  const t = i.get(e);
  i.delete(e), t && t.includes("https://web.whatsapp") && chrome.runtime.sendMessage({ action: "whatsIsClosed" });
}, m = () => {
  try {
    chrome.tabs.onUpdated.removeListener(l), chrome.tabs.onRemoved.removeListener(h);
  } catch (e) {
    console.error("erro ao remover os ouvintes do WhatsIsOpen", e);
  } finally {
    chrome.tabs.onUpdated.addListener(l), chrome.tabs.onRemoved.addListener(h);
  }
}, D = () => {
  chrome.runtime.onMessageExternal.addListener(async (e, t, o) => {
    switch (e.action) {
      // Informa que a extensão foi Instalada
      case "is_instaled":
        o({ success: !0 });
        break;
      case "user_auth":
        s("https://web.whatsapp.com/*", "user_auth_callback", { bearer_token: e.bearer_token }), chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (a) => {
          if (a && a.length > 0) {
            const r = a[0];
            chrome.windows.update(r.windowId, { focused: !0 }), chrome.tabs.update(r.id, { active: !0 });
          }
        }), e.close_painel && t.tab && t.tab.id && setTimeout(() => {
          chrome.tabs.remove(t.tab.id);
        }, 100);
        break;
      case "open_whatsapp":
        await chrome.storage.local.set({
          redirect_painel: {
            bearer: e.bearer,
            timer: Math.floor(Date.now() / 6e4)
          }
        }), chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (a) => {
          if (a && a.length > 0) {
            const r = a[0];
            chrome.windows.update(r.windowId, { focused: !0 }), chrome.tabs.update(r.id, { active: !0 }), s("https://web.whatsapp.com/*", "redirect_painel", {});
          } else
            chrome.tabs.create({ url: "https://web.whatsapp.com/" });
        });
        break;
    }
    return !0;
  });
};
p();
m();
D();
chrome.action.onClicked.addListener(() => {
  p(), m(), c();
});
chrome.runtime.onInstalled.addListener(async function(e) {
  b(e), w(e), p(), U(), m(), k(), e.reason === "update" && f();
});
chrome.runtime.onMessage.addListener((e, t, o) => {
  switch (e.message) {
    case "CRM":
      n("crm");
      break;
    case "FLOW":
      n("fluxo");
      break;
    case "funnil":
      n("funnil");
      break;
    case "promotional":
      chrome.tabs.create({ url: e.path });
      break;
  }
});
