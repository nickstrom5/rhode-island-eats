// Rhode Island Eats brand (provisional, 2026-11-03; Nick picks among scripts/icon-concepts.swift's A, B, C): the app icon is concept B,
// a glass of coffee milk, on Hope blue; the shared Eats Ranked icon style, state-prompts/ICON-STYLE.md, no backing shape.
// Usage, from ri-eats/: swift scripts/make-brand.swift   -> RhodeIslandEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let HOPE: UInt32 = 0x1D3F73, TEAL: UInt32 = 0x1C6670, SALT: UInt32 = 0xF7F5EF, GOLD: UInt32 = 0xF2C14E

/// A glass of coffee milk (the state drink) with a white straw. CoreGraphics y-up. Identical to icon-concepts.swift's concept B.
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

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(HOPE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    coffeeMilk(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "RhodeIslandEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): Hope blue, the coffee milk at the left, the name and tagline at the right, and the app's header band
/// along the bottom: Narragansett Bay swells over an anchor-gold strip of sand.
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(HOPE)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    ctx.setFillColor(rgb(GOLD)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: 26))
    ctx.setFillColor(rgb(0x163159))
    var x: CGFloat = 0
    while x < CGFloat(W) {
        ctx.move(to: CGPoint(x: x, y: 26)); ctx.addQuadCurve(to: CGPoint(x: x + 44, y: 26), control: CGPoint(x: x + 22, y: 62)); ctx.closePath(); ctx.fillPath()
        x += 44
    }
    ctx.saveGState(); ctx.translateBy(x: 30, y: 70); coffeeMilk(ctx, 520); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 70) ?? NSFont.boldSystemFont(ofSize: 66)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 38) ?? NSFont.boldSystemFont(ofSize: 34)
    NSAttributedString(string: "RHODE ISLAND EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 540, y: 330))
    NSAttributedString(string: "CLAM SHACKS, WIENERS & MORE", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.949, green: 0.757, blue: 0.306, alpha: 1)]).draw(at: NSPoint(x: 544, y: 272))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
