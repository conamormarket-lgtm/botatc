import React, { useState, useMemo } from "react"
import { Search, ChevronDown, ChevronUp, MapPin, Phone, MessageCircle, AlertTriangle, CheckCircle2, Circle, User } from "lucide-react"
import { Modal } from "../ui/modal"
import { useOrders } from "../../contexts/orders-context"
import { formatMoneyStrict, formatNumeroPedido, getThemeHoverColor, getCleanImageUrls, matchesBusquedaPedido } from "../../lib/utils"
import { obtenerValorCampo } from "../../lib/business-logic"
import { DesignGallery } from "../ui/design-gallery"

// Definición de las etapas del flujo de pedido
export const ETAPAS = [
    { key: "diseño", label: "Diseño", color: "#A855F7" },
    { key: "impresion", label: "Impresión", color: "#EAB308" },
    { key: "preparacion", label: "Preparación", color: "#3B82F6" },
    { key: "estampado", label: "Estampado", color: "#F97316" },
    { key: "empaquetado", label: "Empaquetado", color: "#10B981" },
    { key: "reparto", label: "Reparto", color: "#14B8A6" },
    { key: "entregado", label: "Entregado", color: "#22C55E" },
]

// Detectar el índice de la etapa actual dado el estadoGeneral
export function getStageIndex(estadoGeneral: string): number {
    const s = (estadoGeneral || "").toLowerCase()
    if (s.includes("entregado")) return 6
    if (s.includes("reparto")) return 5
    if (s.includes("empaquetado")) return 4
    if (s.includes("estampado")) return 3
    if (s.includes("preparac") || s.includes("listo para")) return 2
    if (s.includes("impres")) return 1
    if (s.includes("diseño")) return 0
    return -1
}

// Helper: formatea una fecha como "15 feb 2025"
export function fmtFechaCorta(d: any): string | null {
    if (!d) return null
    try {
        const date = d?.toDate ? d.toDate() : new Date(d)
        if (isNaN(date.getTime())) return null
        return date.toLocaleDateString("es-PE", { day: "2-digit", month: "short", year: "numeric" })
    } catch { return null }
}

// Barra de progreso de etapas
export function OrderProgressBar({ estadoGeneral, pedido }: { estadoGeneral: string; pedido?: any }) {
    const currentIdx = getStageIndex(estadoGeneral)

    return (
        <div className="mt-1 mb-2">
            <div className="flex items-start justify-between relative">
                {/* Línea de fondo */}
                <div
                    className="absolute top-4 left-0 right-0 h-1 bg-slate-200 rounded-full z-0"
                    style={{ margin: "0 calc(100% / 14)" }}
                />
                {/* Línea de progreso */}
                {currentIdx >= 0 && (
                    <div
                        className="absolute top-4 left-0 h-1 rounded-full z-0 transition-all duration-700"
                        style={{
                            width: currentIdx === 0
                                ? "calc(100% / 14)"
                                : `calc(${currentIdx} / ${ETAPAS.length - 1} * (100% - 100% / 7) + 100% / 14)`,
                            background: ETAPAS[currentIdx]?.color || "#6B7280",
                            margin: "0 calc(100% / 14)",
                            maxWidth: "calc(100% - 100% / 7)",
                        }}
                    />
                )}
                {ETAPAS.map((etapa, idx) => {
                    const isPast = idx < currentIdx
                    const isCurrent = idx === currentIdx
                    const isFuture = idx > currentIdx

                    // Obtener la fecha de entrada de la etapa desde el pedido
                    // "entregado" no tiene sub-objeto propio, usa reparto.fechaFinalizado
                    let fechaEntrada: string | null = null
                    if (pedido) {
                        if (etapa.key === "entregado") {
                            fechaEntrada = fmtFechaCorta(pedido.reparto?.fechaFinalizado)
                        } else {
                            fechaEntrada = fmtFechaCorta(pedido[etapa.key]?.fechaEntrada)
                        }
                    }

                    return (
                        <div
                            key={etapa.key}
                            className="flex flex-col items-center z-10"
                            style={{ width: `${100 / ETAPAS.length}%` }}
                        >
                            {/* Círculo indicador */}
                            <div
                                className="w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300 shadow-sm"
                                style={{
                                    backgroundColor: isFuture ? "#F1F5F9" : etapa.color,
                                    borderColor: isFuture ? "#CBD5E1" : etapa.color,
                                    boxShadow: isCurrent
                                        ? `0 0 0 4px ${etapa.color}33, 0 2px 8px ${etapa.color}55`
                                        : undefined,
                                    transform: isCurrent ? "scale(1.18)" : "scale(1)",
                                }}
                            >
                                {isPast ? (
                                    <CheckCircle2 className="w-4 h-4 text-white" strokeWidth={2.5} />
                                ) : isCurrent ? (
                                    <div className="w-2.5 h-2.5 rounded-full bg-white" />
                                ) : (
                                    <div className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                                )}
                            </div>

                            {/* Etiqueta */}
                            <span
                                className="mt-1.5 text-center leading-tight"
                                style={{
                                    fontSize: "0.6rem",
                                    fontWeight: isCurrent ? 800 : isPast ? 600 : 400,
                                    color: isFuture
                                        ? "#94A3B8"
                                        : isCurrent
                                            ? etapa.color
                                            : "#475569",
                                    whiteSpace: "nowrap",
                                }}
                            >
                                {etapa.label}
                            </span>

                            {/* Fecha de entrada */}
                            <span
                                className="mt-0.5 text-center leading-tight"
                                style={{
                                    fontSize: "0.55rem",
                                    color: fechaEntrada
                                        ? (isCurrent ? etapa.color : "#64748B")
                                        : "transparent",
                                    whiteSpace: "nowrap",
                                    minHeight: "0.7rem",
                                }}
                                title={fechaEntrada || ""}
                            >
                                {fechaEntrada || "–"}
                            </span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

// Tarjeta de resultado de pedido individual (con su propio acordeón)
export function PedidoResultCard({
    pedido,
    getTotal,
    getSaldoPendiente,
    formatDescPrendas,
    getImages,
    getStatusColor,
    copyToClipboard,
    openWhatsApp,
    defaultExpanded,
}: {
    pedido: any
    getTotal: (p: any) => number
    getSaldoPendiente: (p: any) => number
    formatDescPrendas: (p: any) => string
    getImages: (p: any) => string[]
    getStatusColor: (s: string) => string
    copyToClipboard: (text: string, label: string) => void
    openWhatsApp: (phone: string) => void
    defaultExpanded: boolean
}) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded)

    return (
        <div className="rounded-xl overflow-hidden shadow-lg border border-slate-200 bg-white shadow-slate-200/50">
            {/* Header card */}
            <div
                className="flex items-center justify-between p-4 bg-blue-500 text-white cursor-pointer select-none"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <h3 className="font-bold text-lg leading-none">Pedido: #{formatNumeroPedido(pedido)}</h3>
                <div className="flex items-center gap-3">
                    <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-sm ${getStatusColor(pedido.estadoGeneral)}`}>
                        {pedido.estadoGeneral || "DESCONOCIDO"}
                    </span>
                    {isExpanded ? <ChevronUp className="h-5 w-5 opacity-80" /> : <ChevronDown className="h-5 w-5 opacity-80" />}
                </div>
            </div>

            {/* Body card */}
            {isExpanded && (
                <div className="p-6">
                    <h4 className="text-xs font-bold text-slate-400 mb-4 tracking-wider uppercase">INFORMACIÓN</h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5 mb-6 text-sm text-slate-700 leading-relaxed font-medium">
                        <div className="flex flex-col gap-1">
                            <div>
                                <span className="font-extrabold text-slate-900 drop-shadow-sm">Cliente:</span> {pedido.clienteNombre || "No especificado"}
                            </div>
                            <div className="text-slate-500 font-normal">
                                (DNI: {pedido.clienteNumeroDocumento || "N/A"} / Tel: {pedido.clienteContacto || "No especificado"})
                            </div>
                        </div>

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Destino:</span> {pedido.envioDestino || "No disponible"}
                        </div>

                        {(pedido.envioDepartamento || pedido.envioProvincia || pedido.envioDistrito) && (
                            <div className="md:col-span-2 flex flex-col gap-1 rounded-lg bg-slate-50 border border-slate-200 px-4 py-2.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Datos de Envío</span>
                                <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm font-medium text-slate-700">
                                    {pedido.envioDepartamento && (
                                        <div>
                                            <span className="font-extrabold text-slate-900">Departamento:</span> {pedido.envioDepartamento}
                                        </div>
                                    )}
                                    {pedido.envioProvincia && (
                                        <div>
                                            <span className="font-extrabold text-slate-900">Provincia:</span> {pedido.envioProvincia}
                                        </div>
                                    )}
                                    {pedido.envioDistrito && (
                                        <div>
                                            <span className="font-extrabold text-slate-900">Distrito:</span> {pedido.envioDistrito}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Vendedor:</span> {pedido.vendedor || "No especificado"}
                        </div>

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Fecha de Venta:</span>{" "}
                            {(() => {
                                const raw = pedido.createdAt ?? pedido.fechaRegistro
                                if (!raw) return "No disponible"
                                try {
                                    const d = raw?.toDate ? raw.toDate() : new Date(raw)
                                    if (isNaN(d.getTime())) return "No disponible"
                                    return d.toLocaleDateString("es-PE", { day: "2-digit", month: "short", year: "numeric" })
                                } catch { return "No disponible" }
                            })()}
                        </div>

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Tallas/Desc:</span> {formatDescPrendas(pedido)}
                        </div>

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Adelantado:</span> S/ {formatMoneyStrict(pedido.montoAdelanto || 0)}
                        </div>

                        <div>
                            <span className="font-extrabold text-slate-900 drop-shadow-sm">Total:</span> <span className="text-base text-slate-800">S/ {formatMoneyStrict(getTotal(pedido))}</span>
                        </div>

                        {/* Saldo pendiente (monto que se debe) */}
                        <div className="md:col-span-2">
                            <div
                                className="flex items-center gap-3 rounded-xl px-4 py-3 border"
                                style={{
                                    backgroundColor: getSaldoPendiente(pedido) === 0
                                        ? "#F0FDF4"
                                        : "#FFF7ED",
                                    borderColor: getSaldoPendiente(pedido) === 0
                                        ? "#BBF7D0"
                                        : "#FED7AA",
                                }}
                            >
                                <div
                                    className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-base font-black"
                                    style={{
                                        backgroundColor: getSaldoPendiente(pedido) === 0
                                            ? "#22C55E"
                                            : "#F97316",
                                        color: "white",
                                    }}
                                >
                                    {getSaldoPendiente(pedido) === 0 ? "✓" : "S/"}
                                </div>
                                <div className="flex flex-col">
                                    <span
                                        className="text-xs font-bold uppercase tracking-wider"
                                        style={{
                                            color: getSaldoPendiente(pedido) === 0
                                                ? "#16A34A"
                                                : "#C2410C",
                                        }}
                                    >
                                        {getSaldoPendiente(pedido) === 0
                                            ? "PEDIDO PAGADO"
                                            : "SALDO PENDIENTE"}
                                    </span>
                                    <span
                                        className="text-lg font-extrabold"
                                        style={{
                                            color: getSaldoPendiente(pedido) === 0
                                                ? "#15803D"
                                                : "#EA580C",
                                        }}
                                    >
                                        {getSaldoPendiente(pedido) === 0
                                            ? "Cancelado al 100%"
                                            : `S/ ${formatMoneyStrict(getSaldoPendiente(pedido))}`}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {pedido.notasDiseño && (
                        <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50/60 p-4">
                            <h4 className="text-xs font-bold text-amber-700 mb-2 tracking-wider uppercase flex items-center gap-1.5">
                                <AlertTriangle className="w-3.5 h-3.5" />
                                NOTAS DE DISEÑO
                            </h4>
                            <p className="text-sm text-amber-900 whitespace-pre-wrap font-medium">
                                {pedido.notasDiseño}
                            </p>
                        </div>
                    )}

                    <h4 className="text-xs font-bold text-slate-400 mb-4 tracking-wider uppercase border-t border-slate-100 pt-5">GALERÍA DE DISEÑOS</h4>

                    <DesignGallery urlImagen={pedido.diseño?.urlImagen} />

                    {pedido.etiquetaEmpaquetado && (
                        <div className="mb-6 mt-6 rounded-xl border-2 border-red-300 bg-red-50 p-4 shadow-md animate-in fade-in zoom-in duration-300">
                            <h4 className="text-xs font-black text-red-600 mb-2 tracking-widest uppercase flex items-center gap-1.5 drop-shadow-sm">
                                <AlertTriangle className="w-5 h-5" />
                                ETIQUETA / ESTADO
                            </h4>
                            <p className="text-xl font-black text-red-600 uppercase tracking-widest drop-shadow-sm">
                                {pedido.etiquetaEmpaquetado}
                            </p>
                        </div>
                    )}

                    {/* Barra de progreso de etapas */}
                    <div className="pt-5 border-t border-slate-100">
                        <h4 className="text-xs font-bold text-slate-400 mb-4 tracking-wider uppercase">ETAPA DEL PEDIDO</h4>
                        <OrderProgressBar estadoGeneral={pedido.estadoGeneral} pedido={pedido} />
                    </div>

                    {/* Responsables por Etapa */}
                    {(() => {
                        const diseñador = pedido.diseño?.diseñadorNombre
                        const impresor = pedido.impresion?.operador || pedido.impresion?.operadorNombre
                        const preparador = pedido.preparacion?.operador || pedido.preparacion?.operadorNombre
                        const estampador = pedido.estampado?.operador || pedido.estampado?.operadorNombre
                        const empaquetador = pedido.empaquetado?.operador || pedido.empaquetado?.operadorNombre
                        const hayAlguno = diseñador || impresor || preparador || estampador || empaquetador
                        if (!hayAlguno) return null
                        const ETAPA_RESP = [
                            { label: "Diseño", color: "#A855F7", bg: "#F5F3FF", border: "#DDD6FE", value: diseñador },
                            { label: "Impresión", color: "#EAB308", bg: "#FEFCE8", border: "#FEF08A", value: impresor },
                            { label: "Preparación", color: "#3B82F6", bg: "#EFF6FF", border: "#BFDBFE", value: preparador },
                            { label: "Estampado", color: "#F97316", bg: "#FFF7ED", border: "#FED7AA", value: estampador },
                            { label: "Empaquetado", color: "#10B981", bg: "#F0FDF4", border: "#BBF7D0", value: empaquetador },
                        ]
                        return (
                            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 mt-5">
                                <h4 className="text-xs font-bold text-slate-400 mb-3 tracking-wider uppercase flex items-center gap-1.5">
                                    <User className="w-3.5 h-3.5 text-slate-400" />
                                    RESPONSABLES POR ETAPA
                                </h4>
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                                    {ETAPA_RESP.map((et) => (
                                        <div
                                            key={et.label}
                                            className="flex flex-col gap-0.5 rounded-lg px-3 py-2 border"
                                            style={{ backgroundColor: et.value ? et.bg : "#F8FAFC", borderColor: et.value ? et.border : "#E2E8F0" }}
                                        >
                                            <span
                                                className="text-[10px] font-bold uppercase tracking-wider"
                                                style={{ color: et.value ? et.color : "#94A3B8" }}
                                            >
                                                {et.label}
                                            </span>
                                            <span
                                                className="text-sm font-semibold truncate"
                                                style={{ color: et.value ? "#1E293B" : "#CBD5E1" }}
                                                title={et.value || "Sin asignar"}
                                            >
                                                {et.value || "—"}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    })()}
                </div>
            )}
        </div>
    )
}

export function BuscarPedidoModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
    const { orders } = useOrders()
    const [searchTerm, setSearchTerm] = useState("")
    const [searchExecuted, setSearchExecuted] = useState("")
    const [errorMsg, setErrorMsg] = useState("")

    // Los resultados se recalculan reactivamente cuando `orders` cambia,
    // de modo que si un pedido cambia de etapa (diseño → cobranza, etc.)
    // la tarjeta del resultado lo refleja en vivo sin necesidad de recargar.
    const resultadosPedidos = useMemo(() => {
        if (!searchExecuted.trim()) return []
        return orders.filter((p: any) => matchesBusquedaPedido(p, searchExecuted.trim()))
    }, [orders, searchExecuted])

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        setErrorMsg("")

        if (!searchTerm.trim()) {
            setErrorMsg("Ingresa un número de pedido o DNI para buscar.")
            return
        }

        setSearchExecuted(searchTerm.trim())

        // Error diferido: si tras ejecutar no hay resultados, se muestra en el próximo render
    }

    const copyToClipboard = (text: string, label: string) => {
        if (!text || text === "No disponible") {
            alert(`No hay ${label.toLowerCase()} disponible para copiar.`)
            return
        }
        navigator.clipboard.writeText(text)
            .then(() => alert(`${label} copiado al portapapeles!`))
            .catch(err => console.error('Failed to copy: ', err))
    }

    const openWhatsApp = (phone: string) => {
        if (!phone || phone === "No disponible") {
            alert("El número de teléfono no está disponible.")
            return
        }

        let cleanedPhone = phone.replace(/\D/g, '')
        if (cleanedPhone.length === 9) {
            cleanedPhone = "51" + cleanedPhone
        }

        window.open(`https://wa.me/${cleanedPhone}`, "_blank")
    }

    const getTotal = (pedido: any) => {
        const totalA = Number(pedido.cobranza?.montoTotalAnadidos ?? pedido.diseño?.montoTotalAnadidos) || 0
        const totalC = Number(pedido.cobranza?.montoTotalComplementos ?? pedido.diseño?.montoTotalComplementos) || 0
        return (pedido.montoTotal || 0) + (pedido.montoEnvio || 0) + (pedido.costoDiseñoTotal || 0) + totalA + totalC
    }

    // Saldo pendiente: leer directamente del campo calculado de la Deuda Total global
    const getSaldoPendiente = (pedido: any) => {
        let deuda = Number(obtenerValorCampo(pedido, "deudaTotal"))
        if (!isNaN(deuda)) return Math.max(0, deuda)
        // Fallback robusto en caso de error en parser
        return pedido.montoPendiente ?? Math.max(0, getTotal(pedido) - (pedido.montoAdelanto || 0))
    }

    // Renderizar prendas como descripción
    const formatDescPrendas = (pedido: any) => {
        if (Array.isArray(pedido.prendas) && pedido.prendas.length > 0) {
            return pedido.prendas.map((p: any) => `${p.tipoPrenda} ${p.color} (${p.talla})`).join(' - ')
        }
        if (pedido.productos && Array.isArray(pedido.productos) && pedido.productos.length > 0) {
            const prendasProd = pedido.productos.flatMap((p: any) => {
                if (Array.isArray(p.detallesPrenda) && p.detallesPrenda.length > 0) {
                    return p.detallesPrenda.map((d: any) => `${d.tipoPrenda} ${d.color} (${d.talla})`)
                }
                return []
            })
            if (prendasProd.length > 0) return prendasProd.join(' - ')
            return pedido.productos.map((p: any) => p.nombre || p.tipoProducto || "Producto").join(' - ')
        }
        if (pedido.talla) {
            return pedido.talla
        }
        return "No especificado"
    }

    // Obtener URLs de imágenes para la galería
    const getImages = (pedido: any) => {
        return getCleanImageUrls(pedido.diseño?.urlImagen)
    }

    // Render status badge background color based on status text (approximate matching)
    const getStatusColor = (status: string) => {
        const s = (status || "").toLowerCase()
        if (s.includes("estampado")) return "bg-orange-500"
        if (s.includes("preparado") || s.includes("listo para") || s.includes("empaquetado")) return "bg-green-500"
        if (s.includes("diseño")) return "bg-purple-500"
        if (s.includes("cobranza")) return "bg-yellow-500"
        if (s.includes("reparto") || s.includes("entregado")) return "bg-teal-500"
        return "bg-slate-500"
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Buscar Pedido" size="xl">
            <div className="flex flex-col gap-6">
                <form onSubmit={handleSearch} className="flex items-center gap-3">
                    <div className="relative flex-1">
                        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-slate-400" />
                        </div>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="block w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none shadow-sm transition-all bg-slate-50"
                            placeholder="Ej. #6069, o número de DNI..."
                            autoFocus
                        />
                    </div>
                    <button
                        type="submit"
                        className="px-6 py-3 bg-blue-600 text-white rounded-xl shadow-md hover:bg-blue-700 transition font-medium text-lg whitespace-nowrap"
                    >
                        Buscar
                    </button>
                </form>

                {(errorMsg || (searchExecuted && resultadosPedidos.length === 0)) && (
                    <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-200 flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5" />
                        <span className="font-medium">
                            {errorMsg || "No se encontró ningún pedido con ese número de pedido o DNI."}
                        </span>
                    </div>
                )}

                {/* Banner informativo cuando hay múltiples resultados */}
                {resultadosPedidos.length > 1 && (
                    <div className="p-3 bg-blue-50 text-blue-700 rounded-xl border border-blue-200 flex items-center gap-2 text-sm font-medium">
                        <Search className="h-4 w-4 flex-shrink-0" />
                        Se encontraron <span className="font-extrabold mx-1">{resultadosPedidos.length}</span> pedidos para el DNI o teléfono buscado.
                    </div>
                )}

                {/* Renderizar una tarjeta por cada pedido encontrado */}
                {resultadosPedidos.map((pedido, idx) => (
                    <PedidoResultCard
                        key={pedido.id || pedido.numeroPedido || idx}
                        pedido={pedido}
                        getTotal={getTotal}
                        getSaldoPendiente={getSaldoPendiente}
                        formatDescPrendas={formatDescPrendas}
                        getImages={getImages}
                        getStatusColor={getStatusColor}
                        copyToClipboard={copyToClipboard}
                        openWhatsApp={openWhatsApp}
                        defaultExpanded={idx === 0}
                    />
                ))}
            </div>
        </Modal>
    )
}
