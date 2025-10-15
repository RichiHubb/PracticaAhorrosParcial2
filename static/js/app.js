function activeMenuOption(href) {
    // Clear active state from all nav links in known nav containers
    $(".nav-sidebar .nav-link, .nav-pills .nav-link, .app-menu .nav-link")
    .removeClass("active")
    .removeAttr('aria-current')

    href = href || "/"

    // Try several selectors: exact match first, then starts-with (to handle routes with params)
    var selector = [
        `.nav-sidebar .nav-link[href="${href}"]`,
        `.nav-pills .nav-link[href="${href}"]`,
        `.app-menu .nav-link[href="${href}"]`,
        `.nav-sidebar .nav-link[href^="${href}"]`,
        `.nav-pills .nav-link[href^="${href}"]`,
        `.app-menu .nav-link[href^="${href}"]`
    ].join(',')

    var $link = $(selector).first()
    if ($link && $link.length) {
        $link.addClass('active').attr('aria-current', 'page')
    } else {
        // Fallback: try any link that contains the path (looser match)
        var path = href.replace(/^#/, '')
        var $loose = $(`.nav-sidebar .nav-link[href*="${path}"], .nav-pills .nav-link[href*="${path}"]`).first()
        if ($loose && $loose.length) {
            $loose.addClass('active').attr('aria-current', 'page')
        }
    }
}

// Avoid redeclaration if this file is included multiple times.
// Try to reuse an existing module or window.app if present.
var app;
if (window.app) {
    app = window.app;
} else {
    try {
        // If the module already exists, this will return it.
        app = angular.module("angularjsApp");
    } catch (e) {
        // Module doesn't exist yet — create it with dependencies.
        app = angular.module("angularjsApp", ["ngRoute"]);
    }
    window.app = app;
}
app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
    .when("/", {
      templateUrl: "top_section.html"
    })
    .when("/login", {
        templateUrl: "/login",
        controller: "loginCtrl"
    })
    .when("/productos", {
        templateUrl: "/productos",
        controller: "productosCtrl"
    })
    .when("/etiquetas", {
        templateUrl: "/etiquetas",
        controller: "etiquetasCtrl"
    })
    .when("/cuentas", {
        templateUrl: "/cuentas",
        controller: "cuentasCtrl"
    })
    .when("/movimientos", {
        templateUrl: "/movimientos",
        controller: "movimientosCtrl"
    })
   .when("/movimientosEtiquetas", { 
        templateUrl: "/movimientosEtiquetas", 
        controller: "movimientosetiquetasCtrl" 
    })
    .when("/notasFinancieras", {
        templateUrl: "/notasFinancieras",
        controller: "notasfinancierasCtrl"
    })
    .otherwise({
        redirectTo: "/"
    })
})
app.run(["$rootScope", "$location", "$timeout", function($rootScope, $location, $timeout) {
    

    function actualizarFechaHora() {
        // Use window-scoped variables to avoid redeclaration if this file is
        // included multiple times (prevents 'redeclaration of let' errors).
        window.DateTime = window.DateTime || luxon.DateTime
        window.lxFechaHora = window.lxFechaHora || null

        window.lxFechaHora = window.DateTime
            .now()
            .setLocale("es")

        $rootScope.angularjsHora = window.lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")
        
        const path = current && current.$$route ? current.$$route.originalPath : '/'

        if (path && path.indexOf("splash") == -1) {
            // Compute a safe hash like #/cuentas to feed into activeMenuOption
            const hash = `#${path}`.replace(/\/\/$/, '')

            // Animate slide based on navigation order when possible
            try {
                const activeIdx = $(".nav-pills .nav-link.active, .nav-sidebar .nav-link.active").first().parent().index()
                const targetIdx = $(`[href^="${hash}"]`).first().parent().index()
                if (activeIdx !== -1 && targetIdx !== -1 && activeIdx != targetIdx) {
                    $rootScope.slide  = "animate__animated animate__faster animate__slideIn"
                    $rootScope.slide += ((activeIdx > targetIdx) ? "Left" : "Right")
                }
            } catch (e) {
                // ignore animation errors
            }

            $timeout(function () {
                $("html").css("overflow-x", "auto")
                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(hash)
        }
    })

}])

app.controller("appCtrl", function ($scope, $http) {
    $("#frmInicioSesion").submit(function (event) {
        event.preventDefault()
        $.post("/iniciarSesion", $(this).serialize(), function (res) {
            try {
                if (res && res.ok) {
                    if (res.redirect) window.location = res.redirect
                    else window.location = '/'
                    return
                }
            } catch (e) {}

            alert("Usuario y/o Contraseña Incorrecto(s)")
        }, 'json')
    })
})
app.controller("productosCtrl", function ($scope, $http) {
    function buscarProductos() {
        $.get("/tbodyProductos", function (trsHTML) {
            $("#tbodyProductos").html(trsHTML)
        })
    }

    buscarProductos()
    
     // Enable pusher logging - don't include this in production
    Pusher.logToConsole = true;

    var pusher = new Pusher('bc1c723155afce8dd187', {
      cluster: 'us2'
    });

     var channel = pusher.subscribe("canalProductos")
    channel.bind("eventoProductos", function(data) {
        // alert(JSON.stringify(data))
        buscarProductos()
    })
    
    $(document).on("submit", "#frmProducto", function (event) {
        event.preventDefault()

        $.post("/producto", {
            id: "",
            nombre: $("#txtNombre").val(),
            precio: $("#txtPrecio").val(),
            existencias: $("#txtExistencias").val(),
        })
    })

    $(document).on("click", ".btn-ingredientes", function (event) {
        const id = $(this).data("id")

        $.get(`/productos/ingredientes/${id}`, function (html) {
            modal(html, "Ingredientes", [
                {html: "Aceptar", class: "btn btn-secondary", fun: function (event) {
                    closeModal()
                }}
            ])
        })
    })
})


app.controller("movimientosCtrl", function ($scope, $http) {
    function buscarMovimientos() {
        $.get("/tbodyMovimientos", function (trsHTML) {
            $("#tbodyMovimientos").html(trsHTML)
        })
    }

    buscarMovimientos()

    Pusher.logToConsole = true
    var pusher = new Pusher('bc1c723155afce8dd187', { cluster: 'us2' })
    var channel = pusher.subscribe("canalMovimientos")
    channel.bind("eventoMovimientos", function(data) {
        buscarMovimientos()
    })

    $(document).on("submit", "#frmMovimiento", function (event) {
        event.preventDefault()
        $.post("/movimiento", {
            id: "",
            descripcion: $("#txtDescripcion").val(),
            monto: $("#txtMonto").val(),
            fecha: $("#txtFecha").val()
        })
    })
})


app.controller("decoracionesCtrl", function ($scope, $http) {
    function buscarDecoraciones() {
        $.get("/tbodyDecoraciones", function (trsHTML) {
            $("#tbodyDecoraciones").html(trsHTML)
        })
    }

    buscarDecoraciones()
    
    // Enable pusher logging - don't include this in production
    Pusher.logToConsole = true

    var pusher = new Pusher("e57a8ad0a9dc2e83d9a2", {
      cluster: "us2"
    })

    var channel = pusher.subscribe("canalDecoraciones")
    channel.bind("eventoDecoraciones", function(data) {
        // alert(JSON.stringify(data))
        buscarDecoraciones()
    })

    $(document).on("submit", "#frmDecoracion", function (event) {
        event.preventDefault()

        $.post("/decoracion", {
            id: "",
            nombre: $("#txtNombre").val(),
            precio: $("#txtPrecio").val(),
            existencias: $("#txtExistencias").val(),
        })
    })
})

app.controller("notasfinancierasCtrl", function ($scope, $http) {
    function buscarNotasFinancieras() {
        $.get("/tbodyNotasFinancieras", function (trsHTML) {
            $("#tbodyNotasFinancieras").html(trsHTML)
        })
    }

    buscarNotasFinancieras()

    var pusher = new Pusher('bc1c723155afce8dd187', { cluster: 'us2' });
    var channel = pusher.subscribe("canalNotasFinancieras");
    channel.bind("eventoNotasFinancieras", function(data) {
        buscarNotasFinancieras()
    });
    
    $(document).on("submit", "#frmNotaFinanciera", function (event) {
        event.preventDefault()
        $.post("/notafinanciera", {
            idNota: "",
            titulo: $("#txtTitulo").val(),
            descripcion: $("#txtDesc").val(),
        })
    });

     // UPDATE
    $(document).on("click", ".btnEditar", function() {
        const fila = $(this).closest("tr")
        const id = fila.data("id")
        const titulo = fila.find("td:eq(1)").text()
        const descripcion = fila.find("td:eq(2)").text()

        $("#txtTitulo").val(titulo)
        $("#txtDesc").val(descripcion)

        // Cambiar comportamiento del botón Guardar
        $("#frmCuenta").off("submit").submit(function(e) {
            e.preventDefault()
            $.post(`/notafinanciera/${id}`, {
                titulo: $("#txtTitulo").val(),
                descripcion: $("#txtDesc").val()
            }, function() {
                $("#frmCuenta")[0].reset()
                buscarNotasFinancieras()
                restaurarInsertar()
            })
        })
    })

    // DELETE
    $(document).on("click", ".btnEliminar", function() {
        if (!confirm("¿Seguro que deseas eliminar esta nota?")) return

        const id = $(this).closest("tr").data("id")
        $.ajax({
            url: `/notafinanciera/${id}`,
            type: "DELETE",
            success: function() {
                buscarNotasFinancieras()
            }
        })
    })
});

app.controller("movimientosetiquetasCtrl", function ($scope, $http) {
    function buscarMovimientosEtiquetas() {
        $.get("/tbodyMovimientosEtiquetas", function (trsHTML) {
            $("#tbodyMovimientosEtiquetas").html(trsHTML);
        });
    }

    buscarMovimientosEtiquetas();

    var pusher = new Pusher("bc1c723155afce8dd187", { cluster: "us2" });
    var channel = pusher.subscribe("canalMovimientosEtiquetas");
    channel.bind("eventoMovimientosEtiquetas", function () {
        buscarMovimientosEtiquetas();
    });

    $(document).on("submit", "#frmMovimientoEtiqueta", function (event) {
        event.preventDefault();
        $.post("/movimientoetiqueta", {
            idMovimientoEtiqueta: $("#txtIDMovimientoEtiqueta").val(),
            idMovimiento: $("#txtIDMovimiento").val(),
            idEtiqueta: $("#txtIDEtiqueta").val()
        });
    });
});

app.controller("cuentasCtrl", function ($scope, $http) {
    function buscarCuentas() {
        $.get("/tbodyCuentas", function (trsHTML) {
            $("#tbodyCuentas").html(trsHTML)
        })
    }

    buscarCuentas()
    
     // Enable pusher logging - don't include this in production
    Pusher.logToConsole = false;

    var pusher = new Pusher('bc1c723155afce8dd187', {
      cluster: 'us2'
    });

     var channel = pusher.subscribe("canalCuentas")
    channel.bind("eventoCuentas", function(data) {
        buscarCuentas()
    })
    
    $(document).on("submit", "#frmCuenta", function (event) {
        event.preventDefault()

        $.post("/cuenta", {
            id: "",
            nombre: $("#txtNombre").val(),
            balance: $("#txtBalance").val()
        })
    })
})


app.controller("etiquetasCtrl", function ($scope, $http) {
    function buscarEtiquetas() {
        $.get("/tbodyEtiquetas", function (trsHTML) {
            $("#tbodyEtiquetas").html(trsHTML)
        })
    }

    buscarEtiquetas()

    var pusher = new Pusher('bc1c723155afce8dd187', {
      cluster: 'us2'
    });

    var channel = pusher.subscribe("canalEtiquetas")
    channel.bind("eventoEtiquetas", function(data) {
        // alert(JSON.stringify(data))
        buscarEtiquetas()
    })
    
    $(document).on("submit", "#frmEtiqueta", function (event) {
        event.preventDefault()

        $.post("/etiqueta", {
            id: "",
            nombre: $("#txtNombreEtiqueta").val(),
        })
    })
})

app.controller("loginCtrl", function ($scope, $http) {
    $(document).on("submit", "#frmLogin", function (event) {
        event.preventDefault()
        $.post("/iniciarSesion", {
            username: $("#txtUsuario").val(),
            password: $("#txtContrasena").val(),
        }, function(res){
            try {
                if (res && res.ok) {
                    if (res.redirect) window.location = res.redirect
                    else window.location = '/'
                    return
                }
            } catch(e){}

            alert("Usuario y/o Contraseña Incorrecto(s)")
        }, 'json')
    })
})

// Optional logout helper: elements with class .logout-button will POST to /logout
$(document).on('click', '.logout-button', function (e) {
    e.preventDefault()
    $.post('/logout', {}, function(res){
        if (res && res.ok) {
            if (res.redirect) window.location = res.redirect
            else window.location = '/'
        }
    }, 'json')
})


// Guard top-level DateTime and lxFechaHora on the window to avoid
// redeclaration errors if the script is loaded multiple times.
window.DateTime = window.DateTime || luxon.DateTime
window.lxFechaHora = window.lxFechaHora || null

document.addEventListener("DOMContentLoaded", function (event) {
    const configFechaHora = {
        locale: "es",
        weekNumbers: true,
        // enableTime: true,
        minuteIncrement: 15,
        altInput: true,
        altFormat: "d/F/Y",
        dateFormat: "Y-m-d",
        // time_24hr: false
    }

    activeMenuOption(location.hash)
})

// Simple modal helper compatible with Bootstrap 4 / AdminLTE v3
function modal(contentHtml, title, buttons) {
    // remove existing
    $('#modal-message').remove()

    var modalHtml = '<div class="modal fade" id="modal-message" tabindex="-1" role="dialog" aria-hidden="true">'
        + '<div class="modal-dialog modal-dialog-centered" role="document">'
        + '<div class="modal-content">'
        + '<div class="modal-header">'
        + '<h5 class="modal-title">' + (title||'') + '</h5>'
        + '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'
        + '<span aria-hidden="true">&times;</span>'
        + '</button>'
        + '</div>'
        + '<div class="modal-body">' + (contentHtml||'') + '</div>'
        + '<div class="modal-footer"></div>'
        + '</div></div></div>'

    $('body').append(modalHtml)

    if (Array.isArray(buttons)) {
        buttons.forEach(function(b){
            var btn = $('<button type="button" class="btn"></button>')
            if (b.class) btn.addClass(b.class)
            btn.html(b.html || 'OK')
            if (b.dismiss) btn.attr('data-dismiss', 'modal')
            if (typeof b.fun === 'function') btn.on('click', b.fun)
            $('#modal-message .modal-footer').append(btn)
        })
    }

    $('#modal-message').modal('show')
}

function closeModal() {
    $('#modal-message').modal('hide')
}































