import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, wieners, clams, fedhill, strips, sweets, portuguese, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // downtown Providence (Kennedy Plaza), so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 41.8240, longitude: -71.4128)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Olneyville New York System", "Providence"), pick("Aunt Carrie's", "Narragansett"), pick("Angelo's Restaurant", "Providence")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "wieners": open(.wieners)
        case "clams":
            // from Galilee (Great Island Rd), Narragansett
            model.screenshotLocation = CLLocation(latitude: 41.3790, longitude: -71.5120)
            open(.clams)
        case "fedhill":
            // from DePasquale Square on Atwells Avenue
            model.screenshotLocation = CLLocation(latitude: 41.8205, longitude: -71.4268)
            open(.fedHill)
        case "strips": open(.strips)
        case "sweets": open(.sweets)
        case "portuguese": open(.portuguese)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Olneyville New York System on Plainfield Street: hand-checked, a James Beard America's Classic, with its note
            open(.wieners)
            if let p = pick("Olneyville New York System", "Providence") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Angelo's Restaurant", "Providence")
        case "wieners": pick("Olneyville New York System", "Providence")
        case "clams": pick("Aunt Carrie's", "Narragansett")
        case "fedhill": pick("Angelo's Restaurant", "Providence")
        case "strips": pick("D. Palmieri's Bakery", "Johnston")
        case "sweets": pick("Gray's Ice Cream", "Tiverton")
        case "portuguese": pick("Cafe Alma", "East Providence")
        case "map": pick("Gift Horse", "Providence")
        case "honors": pick("Al Forno Restaurant", "Providence")
        case "oldest": pick("White Horse Tavern", "Newport")
        case "saved": pick("Aunt Carrie's", "Narragansett")
        case "about": nil
        default: pick("Evelyn's Drive-In", "Tiverton")
        }
        model.selectedPlace = place
    }
}
