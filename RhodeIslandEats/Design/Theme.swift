import SwiftUI
import UIKit
import CoreText

/// Rhode Island flag palette (provisional, 2026-11-03; Nick decides, playbook/05-naming.md), light only: Hope blue #1D3F73 (10.4:1 on
/// white) for titles, tint and accents; bay teal #1C6670 (white on it 6.6:1) for the hand-checked guide cards under white text and
/// for honor chips; anchor gold #F2C14E only as a pin and card fill under dark text (gold text on white is 1.7:1, so never text on
/// it); sea-salt white surfaces. No team colors (most fans follow Boston's; Friars vs Rams splits the college fans). The names
/// `green`/`gold` are kept from Wisconsin Eats so the shared views read the same; here `green` is Hope blue and `gold` is bay teal.
enum Theme {
    static let green = Color(hex: 0x1D3F73)      // Hope blue: titles, tint, primary text accents
    static let green2 = Color(hex: 0x2A5590)
    static let gold = Color(hex: 0x1C6670)       // bay teal: card fills under white text, chips
    static let goldSoft = Color(hex: 0xD6ECEE)   // soft teal
    static let lime = Color(hex: 0xF2C14E)       // anchor gold, fills only (hand-checked pins, the title shadow), under dark text
    static let limeSoft = Color(hex: 0xFCEFC9)
    static let sand = Color(hex: 0xF7F5EF)       // the Home background, sea-salt white
    static let red = Color(hex: 0xA8322D)        // honor chips
    static let ink = Color(hex: 0x14213A)
    static let ink2 = Color(hex: 0x2C3A52)
    static let muted = Color(hex: 0x56607A)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF0F3F7)
    static let surface3 = Color(hex: 0xE3E8F0)
    static let rule = Color(hex: 0xE3E8F0)
    static let rule2 = Color(hex: 0xC5CEDC)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Rhode Island Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: a Narragansett Bay shoreline, three rows of Hope-blue swells over an anchor-gold strip of sand.
struct Stripes: View {
    var height: CGFloat = 6

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, band = max(3, h * 0.28)
            let crest = max(6, h * 0.36), step = crest * 2.2
            var p = Path()
            p.move(to: CGPoint(x: 0, y: h - band))
            var x: CGFloat = 0
            while x < w {
                p.addQuadCurve(to: CGPoint(x: x + step, y: h - band), control: CGPoint(x: x + step / 2, y: max(0, h - band - crest * 1.6)))
                x += step
            }
            p.addLine(to: CGPoint(x: x, y: h - band)); p.addLine(to: CGPoint(x: 0, y: h - band)); p.closeSubpath()
            ctx.fill(p, with: .color(Theme.green))
            ctx.fill(Path(CGRect(x: 0, y: h - band, width: w, height: band)), with: .color(Theme.lime))
        }
        .frame(height: height * 3.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
