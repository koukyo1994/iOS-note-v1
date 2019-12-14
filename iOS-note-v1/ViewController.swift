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
        self.imageView.image = UIImage(named: "Keisen.jpg")
        
        let canvas = PKCanvasView(frame: self.imageView.frame)
        view.addSubview(canvas)
        canvas.tool = PKInkingTool(.pen, color: .black, width: 20)
        canvas.backgroundColor = .clear
        canvas.isOpaque = false
        
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
        let drawing = self.canvasView!.drawing
        var image = drawing.image(
            from: self.canvasView!.bounds,
            scale: 1.0)
        image = image.addBackGround()!
        let cgImage = image.cgImage

        let request = VNRecognizeTextRequest(completionHandler: self.detectTextHandler)
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en_US", "ja_JP"]
        request.usesLanguageCorrection = true
        
        let requests = [request]
        let imageRequestHandler = VNImageRequestHandler(cgImage: cgImage!, options: [:])
        try! imageRequestHandler.perform(requests)
    }
    
    func detectTextHandler(request: VNRequest?, error: Error?) {
        guard let observations = request?.results as? [VNRecognizedTextObservation] else {
            return
        }
        
        var texts = [String]()
        var points = [CGPoint]()
        var boundingBoxes = [CGRect]()
        
        let height = self.imageView.bounds.height
        let width = self.imageView.bounds.width
        
        for observation in observations {
            let candidates = 1
            let bbox = observation.boundingBox
            guard let bestCandidate = observation.topCandidates(candidates).first else {
                continue
            }
            
            texts.append(bestCandidate.string)
            points.append(
                CGPoint(
                    x: bbox.origin.x * width,
                    y: (1.0 - bbox.origin.y - bbox.height) * height
            ))
            boundingBoxes.append(
                CGRect(
                    x: bbox.origin.x * width,
                    y: (1.0 - bbox.origin.y - bbox.height - 0.02) * height,
                    width: bbox.width * width,
                    height: bbox.height * height)
            )
        }
        
        var image = self.imageView.getImage()!
        image = image.drawBoundingBox(boundingBoxes: boundingBoxes)!
        self.imageView.image = image.drawDetectedText(texts: texts, points: points)
    }
}

