//
//  Extensions.swift
//  iOS-note-v1
//
//  Created by 荒居秀尚 on 14.12.19.
//  Copyright © 2019 荒居秀尚. All rights reserved.
//

import Foundation
import UIKit
import CoreGraphics
import ImageIO


extension UIImage {
    func addBackGround() -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(self.size, false, 0)
        guard let context = UIGraphicsGetCurrentContext() else {
            return nil
        }
        
        context.setFillColor(CGColor(
            srgbRed: 255,
            green: 255,
            blue: 255,
            alpha: 1.0))
        let rect = CGRect(
            x: 0,
            y: 0,
            width: self.size.width,
            height: self.size.height)
        context.fill(rect)
        
        self.draw(in: CGRect(
            x: 0,
            y: 0,
            width: self.size.width,
            height: self.size.height))
        
        guard let image = UIGraphicsGetImageFromCurrentImageContext() else {
            return nil
        }
        UIGraphicsEndImageContext()
        return image
    }
    
    
    func drawBoundingBox(boundingBoxes bboxes: [CGRect]) -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(self.size, false, 0)
        self.draw(in: CGRect(
            x: 0,
            y: 0,
            width: self.size.width,
            height: self.size.height))

        guard let context = UIGraphicsGetCurrentContext() else {
            return nil
        }
        context.setFillColor(CGColor(srgbRed: 255, green: 217, blue: 0, alpha: 0.3))
        context.fill(bboxes)
        
        guard let image = UIGraphicsGetImageFromCurrentImageContext() else {
            return nil
        }
        UIGraphicsEndImageContext()
        return image
    }
    
    func drawDetectedText(texts: [String], points: [CGPoint]) -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(self.size, false, 0)
        self.draw(in: CGRect(
            x: 0,
            y: 0,
            width: self.size.width,
            height: self.size.height)
        )
        
        let pair = zip(texts, points)
        
        pair.forEach { text, point in
            let writeString = NSAttributedString(
                string: text,
                attributes: [
                    .font: UIFont(name: "Apple SD Gothic Neo", size: 12)!,
                    .foregroundColor: UIColor.black
            ])
            writeString.draw(at: CGPoint(x: point.x, y: point.y - 40))
        }
        
        guard let image = UIGraphicsGetImageFromCurrentImageContext() else {
            return nil
        }
        UIGraphicsEndImageContext()
        return image
    }
}

extension UIView {
    func getImage() -> UIImage? {
        let rect = self.bounds
        UIGraphicsBeginImageContextWithOptions(rect.size, false, 0.0)
        guard let context = UIGraphicsGetCurrentContext() else {
            return nil
        }
        
        self.layer.render(in: context)
        guard let image = UIGraphicsGetImageFromCurrentImageContext() else {
            return nil
        }
        UIGraphicsEndImageContext()
        return image
    }
}

