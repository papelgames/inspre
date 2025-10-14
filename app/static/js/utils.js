function imprSelec(nombre, titulo) {
  var ficha = document.getElementById(nombre);
  var ventimp = window.open('', 'popimpr');
  
  ventimp.document.write('<html><head><title>' + titulo + '</title>');
  
  // Agregar referencias a los estilos
  var stylesheets = document.styleSheets;
  for (var i = 0; i < stylesheets.length; i++) {
      var styleSheet = stylesheets[i];
      if (styleSheet.href) {
          ventimp.document.write('<link rel="stylesheet" href="' + styleSheet.href + '">');
      }
  }

  ventimp.document.write('</head><body>');
  
  // Agregar el contenido a imprimir
  ventimp.document.write('<div>' + ficha.innerHTML + '</div>');
  
  ventimp.document.write('</body></html>');
  ventimp.document.close();
  
  ventimp.onload = function () {
      ventimp.print();
      ventimp.close();
  };
}


function evitarCaracter(event, caracterProhibido) {
  var key = String.fromCharCode(event.keyCode);
  if (key === caracterProhibido) {
      event.preventDefault();
      return false;
  }
  return true;
}

const video = document.getElementById("video");
const videoContainer = document.getElementById("videoContainer");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");
const previewContainer = document.getElementById("previewContainer");
const statusDiv = document.getElementById("status");
const formElement = document.getElementById("form");
const capturarBtn = document.getElementById("capturar");
const cambiarCamaraBtn = document.getElementById("cambiarCamara");
const rehacerBtn = document.getElementById("rehacer");
const iniciarCamaraBtn = document.getElementById("iniciarCamara");
const inicioContainer = document.getElementById("inicioContainer");
const controlesContainer = document.getElementById("controlesContainer");

let blobFoto = null;
let stream = null;
let camaraActual = "environment";
let metadatos = {};
let gpsEnProceso = false;
let gpsObtenido = false;

function mostrarStatus(msg, tipo = "info") {
  if (!statusDiv) return; // Si no existe el elemento, no hacer nada
  
  statusDiv.textContent = msg;
  statusDiv.style.color = tipo === "error" ? "red" : tipo === "success" ? "green" : "#666";
  statusDiv.style.backgroundColor = tipo === "error" ? "#ffe6e6" : tipo === "success" ? "#e6ffe6" : "#f0f0f0";
}
// Iniciar cámara
function iniciarCamara(facingMode = "environment") {
  mostrarStatus("Iniciando cámara...");
  
  capturarBtn.disabled = true;
  cambiarCamaraBtn.disabled = true;
  
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    mostrarStatus("Tu navegador no soporta acceso a la cámara", "error");
    return;
  }
  
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
  
  const constraints = {
    video: {
      facingMode: facingMode,
      width: { ideal: 1280, max: 1920 },
      height: { ideal: 720, max: 1080 }
    }
  };
  
  navigator.mediaDevices.getUserMedia(constraints)
    .then(s => {
      stream = s;
      video.srcObject = s;
      
      video.addEventListener('loadedmetadata', () => {
        mostrarStatus("Cámara lista", "success");
        capturarBtn.disabled = false;
        cambiarCamaraBtn.disabled = false;
      }, { once: true });
      
      setTimeout(() => {
        if (video.videoWidth > 0) {
          capturarBtn.disabled = false;
          cambiarCamaraBtn.disabled = false;
        }
      }, 2000);
    })
    .catch(err => {
      let mensaje = "No se pudo acceder a la cámara";
      
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        mensaje = "Permiso denegado. Permite el acceso a la cámara en la configuración.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        mensaje = "No se encontró cámara en el dispositivo.";
      } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
        mensaje = "La cámara está siendo usada por otra aplicación.";
      } else if (err.name === "OverconstrainedError") {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(s => {
            stream = s;
            video.srcObject = s;
            mostrarStatus("Cámara lista", "success");
            capturarBtn.disabled = false;
            cambiarCamaraBtn.disabled = false;
          })
          .catch(() => mostrarStatus("No se pudo acceder a la cámara", "error"));
        return;
      }
      
      mostrarStatus(mensaje, "error");
      capturarBtn.disabled = true;
      cambiarCamaraBtn.disabled = true;
    });
}

// Botón para abrir cámara
iniciarCamaraBtn.addEventListener("click", () => {
  inicioContainer.style.display = "none";
  videoContainer.style.display = "block";
  controlesContainer.style.display = "block";
  iniciarCamara(camaraActual);
  solicitarGeolocalizacion();
});

// Cambiar cámara
cambiarCamaraBtn.addEventListener("click", () => {
  camaraActual = camaraActual === "environment" ? "user" : "environment";
  iniciarCamara(camaraActual);
  mostrarStatus(`Cambiando a cámara ${camaraActual === "user" ? "frontal" : "trasera"}...`);
});

// Capturar foto
capturarBtn.addEventListener("click", async () => {
  if (!stream || !video.videoWidth || video.videoWidth === 0) {
    mostrarStatus("Cámara no está lista. Esperá unos segundos.", "error");
    return;
  }
  
  capturarBtn.disabled = true;
  
  if (gpsEnProceso && !gpsObtenido) {
    mostrarStatus("Esperando GPS...");
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  metadatos.timestamp = new Date().toISOString();
  metadatos.fecha = new Date().toLocaleString('es-AR');
  metadatos.userAgent = navigator.userAgent;
  metadatos.plataforma = navigator.platform;
  metadatos.resolucionPantalla = `${window.screen.width}x${window.screen.height}`;
  metadatos.resolucionVideo = `${video.videoWidth}x${video.videoHeight}`;
  metadatos.camaraUsada = camaraActual === "environment" ? "trasera" : "frontal";
  
  mostrarStatus("Procesando imagen...");
  
  const ctx = canvas.getContext("2d");
  let width = video.videoWidth;
  let height = video.videoHeight;
  
  const maxDimension = 1024;
  if (width > maxDimension || height > maxDimension) {
    if (width > height) {
      height = Math.round(height * (maxDimension / width));
      width = maxDimension;
    } else {
      width = Math.round(width * (maxDimension / height));
      height = maxDimension;
    }
  }
  
  canvas.width = width;
  canvas.height = height;
  ctx.drawImage(video, 0, 0, width, height);
  
  canvas.toBlob(b => {
    if (!b) {
      mostrarStatus("Error al capturar imagen", "error");
      capturarBtn.disabled = false;
      return;
    }
    
    blobFoto = b;
    preview.src = URL.createObjectURL(b);
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    
    videoContainer.style.display = "none";
    controlesContainer.style.display = "none";
    previewContainer.style.display = "block";
    formElement.style.display = "block";
    
    console.log("Metadatos capturados:", metadatos);
    
    let statusMsg = `Foto lista: ${(b.size/1024).toFixed(1)} KB`;
    if (metadatos.geolocalizacion && !metadatos.geolocalizacion.error) {
      statusMsg += ` - GPS: ${metadatos.geolocalizacion.latitud.toFixed(6)}, ${metadatos.geolocalizacion.longitud.toFixed(6)}`;
    } else if (!gpsObtenido) {
      statusMsg += " - GPS no disponible";
    }
    mostrarStatus(statusMsg, "success");
  }, "image/jpeg", 0.7);
});

// Tomar otra foto
rehacerBtn.addEventListener("click", () => {
  videoContainer.style.display = "block";
  controlesContainer.style.display = "block";
  capturarBtn.disabled = false;
  previewContainer.style.display = "none";
  formElement.style.display = "none";
  blobFoto = null;
  metadatos = {};
  gpsObtenido = false;
  mostrarStatus("Lista para nueva captura");
  iniciarCamara(camaraActual);
  solicitarGeolocalizacion();
});

// Solicitar geolocalización
function solicitarGeolocalizacion() {
  if (!navigator.geolocation) {
    console.warn("✗ Geolocalización no disponible");
    metadatos.geolocalizacion = { error: "Geolocalización no disponible en este navegador" };
    return;
  }
  
  gpsEnProceso = true;
  gpsObtenido = false;
  console.log("📍 Solicitando geolocalización...");
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      metadatos.geolocalizacion = {
        latitud: position.coords.latitude,
        longitud: position.coords.longitude,
        precision: position.coords.accuracy,
        altitud: position.coords.altitude,
        velocidad: position.coords.speed,
        rumbo: position.coords.heading,
        timestamp: new Date(position.timestamp).toISOString()
      };
      gpsEnProceso = false;
      gpsObtenido = true;
      console.log("✓ GPS obtenido:", metadatos.geolocalizacion);
    },
    (error) => {
      let errorMsg = "";
      switch(error.code) {
        case error.PERMISSION_DENIED:
          errorMsg = "Permiso denegado por el usuario";
          break;
        case error.POSITION_UNAVAILABLE:
          errorMsg = "Ubicación no disponible";
          break;
        case error.TIMEOUT:
          errorMsg = "Timeout al obtener ubicación";
          break;
        default:
          errorMsg = error.message;
      }
      
      metadatos.geolocalizacion = {
        error: errorMsg,
        codigo: error.code
      };
      gpsEnProceso = false;
      gpsObtenido = false;
      console.warn("✗ Error GPS:", errorMsg);
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 5000
    }
  );
}

// Subir al servidor
formElement.addEventListener("submit", e => {
  e.preventDefault();
  
  if (!blobFoto) {
    mostrarStatus("No hay foto para subir", "error");
    return;
  }
  
  // Agregar el blob al FormData
  const fd = new FormData(formElement);
  fd.set("foto", blobFoto, "foto.jpg");
  fd.append("metadatos", JSON.stringify(metadatos));
  
  mostrarStatus("Subiendo foto y metadatos...");
  const submitBtn = formElement.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  
  // Crear un form temporal para hacer submit tradicional
  const tempForm = document.createElement('form');
  tempForm.method = 'POST';
  tempForm.action = formElement.action;
  tempForm.enctype = 'multipart/form-data';
  
  // Copiar todos los campos del FormData al form temporal
  for (let [key, value] of fd.entries()) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    
    if (value instanceof Blob) {
      // Para el blob, crear un File object
      const file = new File([value], "foto.jpg", { type: "image/jpeg" });
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.name = key;
      fileInput.style.display = 'none';
      
      // Crear DataTransfer para asignar el archivo
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;
      
      tempForm.appendChild(fileInput);
    } else {
      input.value = value;
      tempForm.appendChild(input);
    }
  }
  
  document.body.appendChild(tempForm);
  tempForm.submit();
});

// Detener cámara al salir
window.addEventListener('beforeunload', () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
});