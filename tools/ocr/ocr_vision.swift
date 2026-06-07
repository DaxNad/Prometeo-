import Foundation
import Vision
import AppKit

struct OCRLine: Codable {
    let text: String
    let confidence: Float
}

struct OCRResult: Codable {
    let source_file: String
    let engine: String
    let status: String
    let lines: [OCRLine]
}

let args = CommandLine.arguments

guard args.count >= 2 else {
    print("USO: swift ocr_vision.swift /percorso/immagine.png")
    exit(2)
}

let imagePath = args[1]
let imageURL = URL(fileURLWithPath: imagePath)

guard let nsImage = NSImage(contentsOf: imageURL),
      let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("ERRORE: immagine non leggibile: \(imagePath)")
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = ["it-IT", "en-US"]

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

do {
    try handler.perform([request])
    let observations = request.results ?? []

    let lines: [OCRLine] = observations.compactMap { obs in
        guard let candidate = obs.topCandidates(1).first else { return nil }
        return OCRLine(text: candidate.string, confidence: candidate.confidence)
    }

    let result = OCRResult(
        source_file: imagePath,
        engine: "macOS Vision",
        status: "PREVIEW_ONLY",
        lines: lines
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(result)
    print(String(data: data, encoding: .utf8)!)
} catch {
    print("ERRORE OCR: \(error)")
    exit(1)
}
