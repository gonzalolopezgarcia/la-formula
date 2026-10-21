// Cuánto tiene abiertos los ojos en cada foto: alto / ancho del contorno de cada ojo (Vision, de macOS).
// Uso: swift ojos.swift foto1.png foto2.png …  →  una línea por foto: «ruta <tab> apertura <tab> giro» (-1 = sin cara).
// Abiertos mirando a cámara: ~0,28. Parpadeo o mirando abajo: por debajo de 0,2. Solo macOS (Vision).
// Giro: cuánto tiene la cabeza girada o ladeada (yaw + roll de Vision, en radianes; 0 = de frente).
// De lado la apertura engaña: el ojo se ve más estrecho y da más.
import Foundation
import Vision

func apertura(_ ojo: VNFaceLandmarkRegion2D?) -> Double {
    guard let p = ojo?.normalizedPoints, p.count > 3 else { return -1 }
    let xs = p.map { Double($0.x) }, ys = p.map { Double($0.y) }
    let ancho = xs.max()! - xs.min()!
    return ancho > 0 ? (ys.max()! - ys.min()!) / ancho : -1
}

for ruta in CommandLine.arguments.dropFirst() {
    let pedido = VNDetectFaceLandmarksRequest()
    try? VNImageRequestHandler(url: URL(fileURLWithPath: ruta)).perform([pedido])
    let cara = (pedido.results ?? []).max { $0.boundingBox.width < $1.boundingBox.width }
    let a = apertura(cara?.landmarks?.leftEye), b = apertura(cara?.landmarks?.rightEye)
    let giro = abs(cara?.yaw?.doubleValue ?? 0) + abs(cara?.roll?.doubleValue ?? 0)
    print("\(ruta)\t\(String(format: "%.3f", a < 0 || b < 0 ? -1 : min(a, b)))\t\(String(format: "%.2f", giro))")
}
