// Rhode Island Eats icon concepts (2026-11-03), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat,
// level, centred food on Hope blue #1D3F73, no backing shape, no text or texture.
//   A  a stuffie: a stuffed quahog in its half shell (the inner rim purple, as quahog shells are) with a lemon wedge
//   B  a glass of coffee milk, the state drink
//   C  a hot wiener "all the way": meat sauce, mustard and onions in a steamed bun
// Usage, from ri-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let HOPE: UInt32 = 0x1D3F73

/// A: the stuffie. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's stuffie().
func stuffie(_ c: CGContext, _ s: CGFloat) {
    func P(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
    // the shell: a wide rounded quahog outline with its hinge bump at the back (top)
    let shell = CGMutablePath()
    shell.move(to: P(0.50, 0.735))
    shell.addCurve(to: P(0.855, 0.50), control1: P(0.70, 0.735), control2: P(0.855, 0.66))
    shell.addCurve(to: P(0.50, 0.255), control1: P(0.855, 0.33), control2: P(0.70, 0.255))
    shell.addCurve(to: P(0.145, 0.50), control1: P(0.30, 0.255), control2: P(0.145, 0.33))
    shell.addCurve(to: P(0.50, 0.735), control1: P(0.145, 0.66), control2: P(0.30, 0.735))
    shell.closeSubpath()
    c.setFillColor(rgb(0xEDE7DC)); c.addPath(shell); c.fillPath()
    // the purple inner rim (wampum), then the golden stuffing mounded inside it
    c.setFillColor(rgb(0x6E4F92)); c.fillEllipse(in: CGRect(x: 0.205 * s, y: 0.305 * s, width: 0.59 * s, height: 0.38 * s))
    c.setFillColor(rgb(0xE0A23C)); c.fillEllipse(in: CGRect(x: 0.235 * s, y: 0.325 * s, width: 0.53 * s, height: 0.34 * s))
    // the browned top of the stuffing: one darker crust over the upper half, hard edge
    c.saveGState(); c.addEllipse(in: CGRect(x: 0.235 * s, y: 0.325 * s, width: 0.53 * s, height: 0.34 * s)); c.clip()
    c.setFillColor(rgb(0xB9702A)); c.fillEllipse(in: CGRect(x: 0.18 * s, y: 0.50 * s, width: 0.64 * s, height: 0.32 * s))
    c.restoreGState()
    // the lemon wedge at the front right, one flat yellow (anchor gold)
    let peel = CGMutablePath()
    peel.move(to: P(0.60, 0.215)); peel.addQuadCurve(to: P(0.86, 0.33), control: P(0.80, 0.16)); peel.addLine(to: P(0.60, 0.215)); peel.closeSubpath()
    c.setFillColor(rgb(0xF2C14E)); c.addPath(peel); c.fillPath()
}

/// B: a glass of coffee milk with a white straw.
func coffeeMilk(_ c: CGContext, _ s: CGFloat) {
    func P(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
    c.setStrokeColor(rgb(0xF4F1EA)); c.setLineWidth(0.05 * s); c.setLineCap(.round)
    c.move(to: P(0.56, 0.62)); c.addLine(to: P(0.68, 0.86)); c.strokePath()
    let glass = CGMutablePath()
    glass.move(to: P(0.30, 0.78)); glass.addLine(to: P(0.70, 0.78)); glass.addLine(to: P(0.65, 0.17)); glass.addLine(to: P(0.35, 0.17)); glass.closeSubpath()
    c.setFillColor(rgb(0xDCE6F0)); c.addPath(glass); c.fillPath()
    let milk = CGMutablePath()
    milk.move(to: P(0.315, 0.66)); milk.addLine(to: P(0.685, 0.66)); milk.addLine(to: P(0.645, 0.19)); milk.addLine(to: P(0.355, 0.19)); milk.closeSubpath()
    c.setFillColor(rgb(0xC9976B)); c.addPath(milk); c.fillPath()
    c.setFillColor(rgb(0xE8D2B8)); c.fill(CGRect(x: 0.315 * s, y: 0.62 * s, width: 0.37 * s, height: 0.04 * s))
}

/// C: a hot wiener all the way, level, in a steamed bun.
func wiener(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat) -> CGRect { CGRect(x: x * s, y: y * s, width: w * s, height: h * s) }
    c.setFillColor(rgb(0xF0D6A3)); c.addPath(CGPath(roundedRect: R(0.15, 0.36, 0.70, 0.22), cornerWidth: 0.11 * s, cornerHeight: 0.11 * s, transform: nil)); c.fillPath()
    c.setFillColor(rgb(0xB5482E)); c.addPath(CGPath(roundedRect: R(0.17, 0.48, 0.66, 0.11), cornerWidth: 0.055 * s, cornerHeight: 0.055 * s, transform: nil)); c.fillPath()
    c.setFillColor(rgb(0x7A3B22)); c.addPath(CGPath(roundedRect: R(0.21, 0.55, 0.58, 0.07), cornerWidth: 0.035 * s, cornerHeight: 0.035 * s, transform: nil)); c.fillPath()
    c.setStrokeColor(rgb(0xF2C14E)); c.setLineWidth(0.03 * s); c.setLineCap(.round)
    c.move(to: CGPoint(x: 0.24 * s, y: 0.60 * s))
    for i in 0..<6 { c.addLine(to: CGPoint(x: (0.30 + CGFloat(i) * 0.09) * s, y: (i % 2 == 0 ? 0.63 : 0.59) * s)) }
    c.strokePath()
    c.setFillColor(rgb(0xF4F1EA))
    for x in [0.30, 0.42, 0.55, 0.67] { c.fillEllipse(in: R(CGFloat(x), 0.625, 0.035, 0.03)) }
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(HOPE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", stuffie)
render(1024, out + "/concept-b-1024.png", coffeeMilk)
render(1024, out + "/concept-c-1024.png", wiener)
