//
//  ViewController.swift
//  iOS-note-v1
//
//  Created by 荒居秀尚 on 12.12.19.
//  Copyright © 2019 荒居秀尚. All rights reserved.
//

import UIKit
import PencilKit
import Vision

class ViewController: UIViewController {
    
    var canvasView: PKCanvasView?

    @IBOutlet weak var imageView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()
        
        let canvas = PKCanvasView(frame: self.imageView.frame)
        view.addSubview(canvas)
        canvas.tool = PKInkingTool(.pen, color: .black, width: 20)
        
        self.canvasView = canvas
        
        if let window = UIApplication.shared.windows.first {
            if let toolPicker = PKToolPicker.shared(for: window) {
                toolPicker.addObserver(canvas)
                toolPicker.setVisible(true, forFirstResponder: canvas)
                canvas.becomeFirstResponder()
            }
        }
    }

    
    @IBAction func detectText(_ sender: Any) {
        let image = canvasView!.drawing.image(
            from: canvasView!.bounds,
            scale: 1.0)
        UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
        let cgImage = image.cgImage
        let request = VNRecognizeTextRequest(completionHandler: self.detectTextHandler)
        
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en_US"]
        request.usesLanguageCorrection = false
        
        let requests = [request]
        let imageRequestHandler = VNImageRequestHandler(cgImage: cgImage!, options: [:])
        try! imageRequestHandler.perform(requests)
    }
    
    func detectTextHandler(request: VNRequest?, error: Error?) {
        guard let observations = request?.results as? [VNRecognizedTextObservation] else {
            return
        }
        
        for observation in observations {
            let candidates = 1
            guard let bestCandidate = observation.topCandidates(candidates).first else {
                continue
            }
            print(bestCandidate.string)
            print(bestCandidate.confidence)
        }
    }
}

