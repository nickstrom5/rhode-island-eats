import XCTest
import CoreLocation
@testable import RhodeIslandEats

@MainActor
final class RhodeIslandEatsTests: XCTestCase {

    /// A tiny core file and its statewide detail file, with the same shape as Resources/places.json and Resources/detail-*.json.
    /// "counties" carries the villages a listing names (Wakefield, Block Island); "cities" are the 39 municipalities.
    private func sampleModel() async throws -> AppModel {
        let json = """
        {"v":1,"generated":"2026-11-03","overture_release":"2026-10-21.0","permits_updated":"2025",
         "permits_url":"https://www.arcgis.com/home/item.html?id=e3f9a20ca91d4098b2220f186910baaa",
         "cities":["Providence","Narragansett","Cranston","South Kingstown","New Shoreham","Warwick","Newport"],
         "cuisines":["Hot Dogs & Sausages","Seafood","Italian","Bakery & Sweets","Breakfast & Diner","American & Other"],
         "brands":["Del's Lemonade","Dunkin'"],"counties":["Block Island","Wakefield"],
         "regions":["Rhode Island"],
         "srcs":["official","meta","AllThePlaces","DAC","research"],
         "count":9,"count_restaurants":8,
         "calibration":{"Rhode Island (RIDOH food service licenses with seats, active in 2018)":{"listings":5858,"groups":{"meta_high":{"n":2413,"official":0.448}}}},
         "places":[
          {"id":"a","n":"Olneyville New York System","c":0,"rg":0,"cu":0,"t":1,"s":1,"hc":1,"g":1,"a":"18 Plainfield St","z":"02909","la":41.8197,"lo":-71.4425,
           "h":1,"ip":50,"jbf":"America's Classic 2014","f":1946,"dish":"hot wieners; coffee milk"},
          {"id":"b","n":"Aunt Carrie's","c":1,"rg":0,"cu":1,"t":1,"s":1,"hc":1,"g":130,"a":"1240 Ocean Rd","la":41.3640,"lo":-71.4840,"h":17,"ip":60,
           "jbf":"America's Classic 2007","f":1920,"dish":"clam cakes; chowder"},
          {"id":"c","n":"Dunkin'","c":2,"rg":0,"cu":4,"t":1,"s":2,"b":1,"ch":180,"la":41.78,"lo":-71.44},
          {"id":"d","n":"Angelo's Restaurant","c":0,"rg":0,"cu":2,"t":1,"s":1,"hc":1,"g":4,"a":"141 Atwells Ave","la":41.8213,"lo":-71.4255},
          {"id":"e","n":"Cumberland Farms","c":2,"rg":0,"cu":5,"t":1,"s":1,"v":1,"la":41.77,"lo":-71.45},
          {"id":"f","n":"Brickley's Ice Cream","c":3,"co":1,"rg":0,"cu":3,"t":1,"s":1,"hc":1,"g":64,"a":"322 Main St","la":41.4470,"lo":-71.4960},
          {"id":"g","n":"Gift Horse","c":0,"rg":0,"cu":1,"t":1,"s":1,"hc":1,"h":2,"ip":30,"jbf":"Best Chef: Northeast winner 2025 (Sky Haneul Kim)","a":"272 Westminster St","la":41.8236,"lo":-71.4130},
          {"id":"h","n":"Ballard's","c":4,"co":0,"rg":0,"cu":1,"t":1,"s":1,"a":"42 Water St","la":41.1720,"lo":-71.5560},
          {"id":"i","n":"Warwick Pizza","c":5,"rg":0,"cu":5,"t":1,"s":1,"a":"1 Warwick Ave","la":41.73,"lo":-71.42}
         ]}
        """
        let detail = """
        {"a":{"ph":"(401) 621-9500","w":"olneyvillenewyorksystem.example"},
         "b":{"w":"javascript:alert(1)"},
         "f":{"w":"https://brickleys.example/"}}
        """
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent("ri-test-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let url = dir.appendingPathComponent("places.json")
        try json.data(using: .utf8)!.write(to: url)
        try detail.data(using: .utf8)!.write(to: dir.appendingPathComponent("detail-rhode-island.json"))
        let model = AppModel(defaults: UserDefaults(suiteName: "test-\(UUID().uuidString)")!)
        await model.load(from: url, detailFolder: dir)
        XCTAssertTrue(model.isLoaded, model.loadError ?? "")
        return model
    }

    func testDecodesAndHidesNonRestaurantsByDefault() async throws {
        let m = try await sampleModel()
        XCTAssertEqual(m.places.count, 9)
        XCTAssertEqual(m.restaurantCount, 8)
        XCTAssertFalse(m.list(.all, sort: .name, search: "", here: nil).contains { $0.name == "Cumberland Farms" }, "a convenience-store counter is hidden by default")
        m.filters.includeNonRestaurants = true
        XCTAssertTrue(m.list(.all, sort: .name, search: "", here: nil).contains { $0.name == "Cumberland Farms" })
        XCTAssertEqual(m.permitsUpdated, "2025")
    }

    func testGuidesListOnlyWhatTheyPromise() async throws {
        let m = try await sampleModel()
        XCTAssertEqual(m.list(.wieners, sort: .name, search: "", here: nil).map(\.name), ["Olneyville New York System"])
        XCTAssertEqual(m.list(.clams, sort: .name, search: "", here: nil).map(\.name), ["Aunt Carrie's"])
        XCTAssertEqual(m.list(.fedHill, sort: .name, search: "", here: nil).map(\.name), ["Angelo's Restaurant"])
        XCTAssertEqual(m.list(.sweets, sort: .name, search: "", here: nil).map(\.name), ["Brickley's Ice Cream"])
        XCTAssertEqual(m.list(.oldest, sort: .oldest, search: "", here: nil).map(\.name), ["Aunt Carrie's"], "only places tagged oldest, by founding year")
        XCTAssertEqual(m.list(.honors, sort: .iconic, search: "", here: nil).map(\.name), ["Aunt Carrie's", "Olneyville New York System", "Gift Horse"])
        XCTAssertEqual(m.list(.strips, sort: .name, search: "", here: nil), [], "a guide with nothing hand-checked yet is empty, not padded")
    }

    /// Rhode Island has no statewide liquor list the app can read: no place says it serves alcohol, and none says it doesn't.
    func testNoAlcoholClaimWithoutALicense() async throws {
        let m = try await sampleModel()
        XCTAssertFalse(m.places.contains(where: \.servesAlcohol))
        XCTAssertEqual(m.alcoholLicenseCount, 0)
    }

    func testDatesAreCalendarDays() {
        var utc = Calendar(identifier: .gregorian)
        utc.timeZone = TimeZone(identifier: "UTC")!
        let d = DayFormat.date("2026-06-16")!
        XCTAssertEqual(utc.dateComponents([.year, .month, .day], from: d), DateComponents(year: 2026, month: 6, day: 16))
        XCTAssertTrue(DayFormat.monthYear("2025-09-01")!.contains("2025"))
        XCTAssertNil(DayFormat.date("2026-13-01"))
        XCTAssertEqual(DayFormat.text("2025"), "2025", "a value that isn't a date is shown as it is")
    }

    func testDetailsLoadOnDemand() async throws {
        let m = try await sampleModel()
        let a = await m.detail(for: m.place(id: "a")!)
        XCTAssertEqual(a?.website?.absoluteString, "https://olneyvillenewyorksystem.example", "a bare host gets https://")
        XCTAssertEqual(a?.ph, "(401) 621-9500")
        let b = await m.detail(for: m.place(id: "b")!)
        XCTAssertNil(b?.website, "a javascript: link never becomes a website button")
        let f = await m.detail(for: m.place(id: "f")!)
        XCTAssertEqual(f?.website?.host, "brickleys.example")
        XCTAssertEqual(AppModel.regionSlug("Rhode Island"), "rhode-island")
        let none = await m.detail(for: m.place(id: "c")!)
        XCTAssertNil(none?.website, "a place with no detail row has no website")
    }

    func testSearchWordStartsTownsVillagesAndGuides() async throws {
        let m = try await sampleModel()
        XCTAssertEqual(m.list(.all, sort: .name, search: "olney", here: nil).map(\.name), ["Olneyville New York System"])
        XCTAssertEqual(m.list(.all, sort: .name, search: "narragansett", here: nil).map(\.name), ["Aunt Carrie's"], "a town narrows to it")
        XCTAssertEqual(m.list(.all, sort: .name, search: "wakefield", here: nil).map(\.name), ["Brickley's Ice Cream"], "a village finds its places")
        XCTAssertEqual(m.list(.all, sort: .name, search: "block island", here: nil).map(\.name), ["Ballard's"], "Block Island is New Shoreham")
        XCTAssertEqual(m.list(.all, sort: .name, search: "clam cakes", here: nil).map(\.name), ["Aunt Carrie's"], "a guide word means the guide")
        XCTAssertEqual(m.list(.all, sort: .name, search: "hot wieners", here: nil).map(\.name), ["Olneyville New York System"])
        XCTAssertEqual(m.list(.all, sort: .name, search: "coffee milk", here: nil).map(\.name), ["Olneyville New York System"], "a dish finds who serves it")
        XCTAssertEqual(m.list(.all, sort: .name, search: "🍕", here: nil), [], "an emoji finds nothing, not everything")
        XCTAssertEqual(m.list(.all, sort: .name, search: "warwick ave", here: nil).map(\.name), ["Warwick Pizza"],
                       "an avenue is a street: \u{201C}warwick ave\u{201D} isn't only the town of Warwick")
        XCTAssertEqual(m.list(.all, sort: .name, search: "atwells", here: nil).map(\.name), ["Angelo's Restaurant"])
        XCTAssertEqual(Search.normalize("Phở Tây Đô"), "pho tay do", "letters folding keeps (ø, đ) are folded too")
    }

    func testOutsideRhodeIslandUsesTheOutline() {
        func inside(_ la: Double, _ lo: Double) -> Bool { RhodeIslandOutline.contains(CLLocationCoordinate2D(latitude: la, longitude: lo)) }
        XCTAssertTrue(inside(41.824, -71.413), "Providence"); XCTAssertTrue(inside(41.17, -71.57), "Block Island"); XCTAssertTrue(inside(41.31, -71.857), "Watch Hill")
        XCTAssertTrue(inside(41.49, -71.31), "Newport"); XCTAssertTrue(inside(41.50, -71.37), "Jamestown"); XCTAssertTrue(inside(42.00, -71.51), "Woonsocket")
        XCTAssertTrue(inside(41.51, -71.17), "Little Compton"); XCTAssertTrue(inside(41.38, -71.51), "Galilee"); XCTAssertTrue(inside(41.95, -71.75), "Chepachet")
        XCTAssertFalse(inside(41.70, -71.155), "Fall River"); XCTAssertFalse(inside(41.945, -71.285), "Attleboro"); XCTAssertFalse(inside(41.36, -71.97), "Stonington CT")
        XCTAssertFalse(inside(42.36, -71.06), "Boston"); XCTAssertFalse(inside(41.27, -70.10), "Nantucket")
        XCTAssertFalse(inside(37.33, -122.03), "Cupertino")
    }

    func testBundledData() async throws {
        let m = AppModel(defaults: UserDefaults(suiteName: "bundle-\(UUID().uuidString)")!)
        await m.load()
        XCTAssertTrue(m.isLoaded, m.loadError ?? "")
        XCTAssertGreaterThan(m.restaurantCount, 2_500)
        XCTAssertEqual(m.towns.count, 39, "all 39 cities and towns, no villages or mailing towns among them")
        XCTAssertEqual(m.bibCount, 0, "Rhode Island has no MICHELIN Guide")
        XCTAssertFalse(m.places.contains { $0.michelin != .none })
        XCTAssertGreaterThanOrEqual(m.count(.honors), 6)
        XCTAssertGreaterThanOrEqual(m.count(.wieners), 5)
        XCTAssertGreaterThanOrEqual(m.count(.clams), 10)
        XCTAssertEqual(Set(m.places.map(\.id)).count, m.places.count, "ids are unique")
        for g in Guide.allCases where g.tag != nil {
            XCTAssertTrue(m.places.filter(g.includes).allSatisfy(\.handChecked), "\(g.title) lists only hand-checked places")
        }
        XCTAssertTrue(m.places.contains { $0.name == "Olneyville New York System" && $0.city == "Providence" && $0.jamesBeardLabel == "America's Classic" })
        XCTAssertTrue(m.places.contains { $0.name.hasPrefix("Aunt Carrie") && $0.jamesBeardLabel == "America's Classic" })
        XCTAssertTrue(m.places.contains { $0.name == "White Horse Tavern" && $0.founded == 1673 })
        XCTAssertFalse(m.places.contains { $0.name == "Old Canteen" && $0.address?.hasPrefix("120 Atwells") == true }, "the Old Canteen closed in 2025")
        // Block Island places are in New Shoreham, findable by the island's name
        let island = m.list(.all, sort: .name, search: "block island", here: nil)
        XCTAssertGreaterThan(island.count, 10)
        XCTAssertTrue(island.allSatisfy { $0.city == "New Shoreham" || $0.name.lowercased().contains("block island") })
        XCTAssertEqual(m.alcoholLicenseCount, 0, "no statewide liquor list: unknown, never a claim")
        // no Google-derived data: the data file has no rating, review or price fields at all
        let raw = try String(contentsOf: Bundle.main.url(forResource: "places", withExtension: "json")!, encoding: .utf8)
        for key in ["\"rating\"", "\"reviews\"", "\"price\"", "\"gmap_id\""] { XCTAssertFalse(raw.contains(key), "\(key) must not ship") }
    }

    /// Stable ids: md5(name + ~100 m cell)[:12], never a row number; the bundled detail file decodes and its ids are core ids.
    func testIdsAndBundledDetailFiles() async throws {
        let m = AppModel(defaults: UserDefaults(suiteName: "ids-\(UUID().uuidString)")!)
        await m.load()
        XCTAssertTrue(m.places.allSatisfy { $0.id.count >= 12 && $0.id.prefix(12).allSatisfy(\.isHexDigit) && $0.id.dropFirst(12).allSatisfy { $0 == "x" } })
        let ids = Set(m.places.map(\.id))
        XCTAssertEqual(Set(m.places.compactMap(\.region)), ["Rhode Island"], "one statewide detail file")
        let url = try XCTUnwrap(Bundle.main.url(forResource: "detail-rhode-island", withExtension: "json"))
        let d = try JSONDecoder().decode([String: PlaceDetail].self, from: Data(contentsOf: url))
        XCTAssertTrue(Set(d.keys).isSubset(of: ids), "detail ids are core ids")
        XCTAssertGreaterThan(d.values.filter { $0.website != nil }.count, 1_000, "the detail file carries the checked websites")
    }

    func testBundledDataGuards() async throws {
        let m = AppModel(defaults: UserDefaults(suiteName: "guards-\(UUID().uuidString)")!)
        await m.load()
        XCTAssertTrue(m.isLoaded, m.loadError ?? "")
        XCTAssertEqual(DataGuards.adultVenues(m.places), [], "no strip club under its name")
        XCTAssertEqual(DataGuards.badWebsites(try DataGuards.bundledLinks(m.places)), [], "no directory, Google or news page as a restaurant's website")
        XCTAssertEqual(DataGuards.badNames(m.places), [], "no visible name ending in \u{201C} the\u{201D} or \u{201C} of\u{201D}, or just \u{201C}The\u{201D}")
        XCTAssertEqual(DataGuards.legalNames(m.places), [], "no license holder entity name (\u{201C}… LLC\u{201D}) shown as a place's name")
        XCTAssertEqual(DataGuards.nonRestaurants(m.places), [], "no nail salon, senior home, gun store or gas station among the restaurants")
        XCTAssertEqual(DataGuards.listedTwice(m.places), [], "no place listed twice (same name, street address and town) with pins apart")
        let raw = try DataGuards.bundledLinks(m.places, raw: true)
        XCTAssertGreaterThan(raw.count, 1_000, "the detail file carries websites")
        XCTAssertEqual(DataGuards.notOneURL(raw), [], "every website is one URL, with no spaces")
    }

    /// Each guard above fires on a copy of the bundled data broken the way QA found it elsewhere: a guard that can't fail guards nothing.
    func testGuardsCatchABrokenCopy() async throws {
        let raw = try Data(contentsOf: Bundle.main.url(forResource: "places", withExtension: "json")!)
        var file = try XCTUnwrap(JSONSerialization.jsonObject(with: raw) as? [String: Any])
        var places = try XCTUnwrap(file["places"] as? [[String: Any]])
        let idx = places.indices.filter { places[$0]["v"] == nil }.prefix(7).map { $0 }
        places[idx[2]]["n"] = "Desire Gentlemen's Club"
        // the same place twice, 2 km apart (QA 2026-10-29 P1 #7)
        var twin = places[idx[0]]
        twin["id"] = "twin00000000"
        twin["la"] = ((twin["la"] as? Double) ?? 41.8) + 0.02
        places.append(twin)
        places[idx[3]]["n"] = "Kitchen the"
        places[idx[4]]["n"] = "OCEAN STATE HOSPITALITY GROUP LLC"
        places[idx[5]]["n"] = "Tipsy Nails & Spa"
        places[idx[6]]["n"] = "The Meltdown"
        file["places"] = places
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("places-broken.json")
        try JSONSerialization.data(withJSONObject: file).write(to: url)
        let m = AppModel(defaults: UserDefaults(suiteName: "broken-\(UUID().uuidString)")!)
        await m.load(from: url)
        XCTAssertTrue(m.isLoaded, m.loadError ?? "")
        let id = idx.map { places[$0]["id"] as? String }
        func caught(_ found: [String], _ i: Int, _ what: String) {
            XCTAssertTrue(found.contains { $0.contains("[\(id[i] ?? "?")]") }, "the guard missed \(what)")
        }
        let links = [(name: "A", id: "x1", url: "https://www.yelp.com/biz/some-place"), (name: "B", id: "x2", url: "https://www.providencejournal.com/story/news/2026/03/a-story/"),
                     (name: "C", id: "x3", url: "https://smart.com/menu")]
        XCTAssertEqual(DataGuards.badWebsites(links).count, 2, "the guard catches a Yelp page and a news story, and not smart.com")
        let messy = [(name: "D", id: "x4", url: "https://togoorder.com/web/1754#/ (Order Online)"), (name: "E", id: "x5", url: "https://bubbakoos.com/a,https://bubbakoos.com/b"),
                     (name: "F", id: "x6", url: "https://hammeredharrys.com/locations/las-vegas-fremont-s ."), (name: "G", id: "x7", url: "instagram.com/sharks1413_macon"),
                     (name: "H", id: "x8", url: "https://togoorder.com/web/1754#/"), (name: "I", id: "x9", url: "https://x.example/menu?a=1&b=2#top")]
        XCTAssertEqual(DataGuards.notOneURL(messy).count, 3, "the guard catches a label after a link, two links run together and a stray \" .\", not a bare host")
        caught(DataGuards.adultVenues(m.places), 2, "a gentlemen's club")
        caught(DataGuards.badNames(m.places), 3, "\u{201C}Kitchen the\u{201D}")
        caught(DataGuards.legalNames(m.places), 4, "a license holder's entity name")
        caught(DataGuards.nonRestaurants(m.places), 5, "a nail salon shown as a restaurant")
        caught(DataGuards.nonRestaurants(m.places), 6, "a Denny's delivery-only brand shown as a restaurant (QA 2026-10-29)")
        XCTAssertTrue(DataGuards.listedTwice(m.places).contains { $0.contains("[twin00000000]") || $0.contains("[\(id[0] ?? "?")]") },
                      "the guard missed a place listed twice with pins 2 km apart")
    }
}

/// Checks on the bundled data, written as functions so testGuardsCatchABrokenCopy can prove each one fires.
enum DataGuards {
    /// directories, Google and news sites: matched on the link's host, so "smart.com" isn't "rt.com"
    static let badHosts = #"^https?://([^/?#]*\.)?(yelp\.com|business\.site|google\.com|groupon\.com|yellowpages\.com|tripadvisor\.com|providencejournal\.com|golocalprov\.com|turnto10\.com|wpri\.com|abc6\.com|rimonthly\.com|newportri\.com|bostonglobe\.com|visitrhodeisland\.com|goprovidence\.com|eater\.com|rt\.com)([:/?#]|$)"#

    static func badWebsites(_ links: [(name: String, id: String, url: String)]) -> [String] {
        links.compactMap { l in
            guard l.url.range(of: badHosts, options: [.regularExpression, .caseInsensitive]) != nil else { return nil }
            return "\(l.name) [\(l.id)]: \(l.url)"
        }
    }

    /// every website in the bundled region detail files, with its place's name: as the app opens it, or (raw) exactly as the data writes it
    static func bundledLinks(_ places: [Place], raw: Bool = false) throws -> [(name: String, id: String, url: String)] {
        let names = Dictionary(places.map { ($0.id, $0.name) }, uniquingKeysWith: { a, _ in a })
        var out: [(name: String, id: String, url: String)] = []
        for region in Set(places.compactMap(\.region)) {
            guard let url = Bundle.main.url(forResource: "detail-" + AppModel.regionSlug(region), withExtension: "json") else { continue }
            for (id, d) in try JSONDecoder().decode([String: PlaceDetail].self, from: Data(contentsOf: url)) {
                if let w = raw ? d.w : d.website?.absoluteString { out.append((names[id] ?? "?", id, w)) }
            }
        }
        return out
    }

    /// a website that isn't one web address: a space ("https://togoorder.com/web/1754#/ (Order Online)"), a second link run on
    /// ("https://bubbakoos.com/a,https://bubbakoos.com/b"), or no web host even with https:// given to a bare one, as the app does
    /// (QA 2026-10-28, P1 #7; scripts/qa-site.py's website_problem)
    static func notOneURL(_ links: [(name: String, id: String, url: String)]) -> [String] {
        links.filter { l in
            if l.url.rangeOfCharacter(from: .whitespacesAndNewlines) != nil
                || l.url.range(of: #"(?i)https?://.*https?://|.[,;|]\s*www\."#, options: .regularExpression) != nil { return true }
            guard let u = URL(string: l.url.contains("://") ? l.url : "https://" + l.url), ["http", "https"].contains(u.scheme?.lowercased() ?? ""),
                  let host = u.host, host.contains(".") else { return true }
            return false
        }.map { "\($0.name) [\($0.id)]: \($0.url)" }
    }

    /// the pipeline's widened rule (ohio.py and texas.py after QA 2026-10-29, as ported to rhodeisland.py)
    static let adultNames = #"gentlem[ae]n['’]?s? (?:club|lounge)|strip club|exotic dancer|\bmen['’]?s club|rick['’]?s cabaret|xtc cabaret|baby dolls|spearmint rhino|bikini bar|pt['’]?s showclub|showgirls|centerfolds|treasures? gentlem|\btopless\b|male exotic|\bgold club\b|peppermint hippo|stilettos? cabaret|deja ?vu showgirls|hustler club|penthouse club"#

    /// every permit or license number in the bundled region detail files, by place id
    static func bundledLicenses(_ places: [Place]) throws -> [String: [String]] {
        var out: [String: [String]] = [:]
        for region in Set(places.compactMap(\.region)) {
            guard let url = Bundle.main.url(forResource: "detail-" + AppModel.regionSlug(region), withExtension: "json") else { continue }
            for (id, d) in try JSONDecoder().decode([String: PlaceDetail].self, from: Data(contentsOf: url)) where !d.licenses.isEmpty {
                out[id] = d.licenses.compactMap(\.id)
            }
        }
        return out
    }

    static func adultVenues(_ places: [Place]) -> [String] {
        places.filter { $0.name.range(of: adultNames, options: [.regularExpression, .caseInsensitive]) != nil }.map { "\($0.name) [\($0.id)]" }
    }

    /// a name cut off after "the" or "of" ("Kitchen the", "Wines of") or nothing but "The", among the places shown by default
    static func badNames(_ places: [Place]) -> [String] {
        places.filter { p in
            let n = p.name.trimmingCharacters(in: .whitespaces).lowercased()
            return !p.isVenue && (n.hasSuffix(" the") || n.hasSuffix(" of") || n == "the")
        }.map { "\($0.name) [\($0.id)]" }
    }

    /// a license holder (owner) is never shown; a business name that's still a legal entity shouldn't be either
    static let legalSuffix = #"\b(llc|l\.l\.c|inc|corp|corporation)\.?$"#

    static func legalNames(_ places: [Place]) -> [String] {
        places.filter { !$0.isVenue && $0.name.range(of: legalSuffix, options: [.regularExpression, .caseInsensitive]) != nil }
            .map { "\($0.name) [\($0.id)]" }
    }

    /// businesses that aren't places to eat, among the places shown by default
    /// and delivery-only brands cooked in another restaurant's kitchen: Denny's The Meltdown, The Burger Den and Banda Burrito (QA 2026-10-29)
    static let nonRestaurantNames = #"\bnails?\b|assisted living|gun (?:club|range|shop|store)|shooting range|firearms|petroleum|\bauto (?:repair|parts)\b|^(?:the )?(?:meltdown|burger den)$|banda burrito|tenderfix|pardon my cheesesteak|neighborhood wings"#

    /// the same place twice: one normalized name at one street address in one town, shown by default, pins at least 1 km apart
    /// (QA 2026-10-29 P1 #7; sc-eats' DataGuards.listedTwice)
    static func listedTwice(_ places: [Place]) -> [String] {
        var seen: [String: Place] = [:], out: [String] = []
        for p in places where !p.isVenue {
            guard let a = p.address, !a.isEmpty, let l = p.location else { continue }
            let k = Search.normalize(p.name) + "|" + Search.normalizeAddress(a) + "|" + (p.city ?? "")
            if let q = seen[k], let m = q.location, l.distance(from: m) >= 1_000 { out.append("\(p.name) [\(p.id)] and [\(q.id)]") }
            else { seen[k] = p }
        }
        return out
    }

    static func nonRestaurants(_ places: [Place]) -> [String] {
        places.filter { !$0.isVenue && $0.name.range(of: nonRestaurantNames, options: [.regularExpression, .caseInsensitive]) != nil }
            .map { "\($0.name) [\($0.id)]" }
    }
}

/// pipeline/website_blocklist.json (hacked, taken-over, expired or another business's sites, confirmed by hand in the link sweeps):
/// no link on it may ship in any field of any JSON file the app bundles. The 2026-10-19 QA found the export had only filtered the
/// website field, or nothing, so hijacked links were still in the bundle. Read from the repo, so a new entry needs no code change.
final class LinkBlocklistTests: XCTestCase {
    func testNoBlocklistedLinkInBundledData() throws {
        let entries = try LinkBlocklist.entries()
        XCTAssertFalse(entries.isEmpty, "the blocklist is missing or empty")
        let files = LinkBlocklist.bundledJSON()
        XCTAssertFalse(files.isEmpty, "no bundled JSON found")
        var hits: [String] = []
        for url in files {
            let text = try String(contentsOf: url, encoding: .utf8)
            hits += LinkBlocklist.hits(in: text, entries).map { "\(url.lastPathComponent): \($0)" }
        }
        XCTAssertEqual(hits, [], "blocklisted links in the app's bundled data")
    }

    /// The guard fires on a copy of the bundled data broken three ways: a blocklisted domain, its subdomain, and a "url" entry.
    func testBlocklistGuardCatchesABrokenCopy() throws {
        let entries = try LinkBlocklist.entries()
        let file = try XCTUnwrap(LinkBlocklist.bundledJSON().max { (try? $0.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) ?? 0 < (try? $1.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) ?? 0 })
        let text = try String(contentsOf: file, encoding: .utf8)
        let domain = try XCTUnwrap(entries.first { ($0["match"] as? String ?? "domain") == "domain" }?["domain"] as? String)
        let fake: [[String: Any]] = entries + [["match": "url", "url": "https://example.org/hacked-page"]]
        let before = LinkBlocklist.hits(in: text, fake).count
        let broken = text + "{\"w\":\"https://www.\(domain)/menu\"}{\"src\":\"http://shop.\(domain)/\"}{\"w\":\"https://example.org/hacked-page/\"}"
        XCTAssertEqual(LinkBlocklist.hits(in: broken, fake).count, before + 3, "a domain, a subdomain and a url entry are all caught")
        XCTAssertEqual(LinkBlocklist.hits(in: "{\"w\":\"https://not\(domain)/\"}", entries), [], "a host that only ends with the domain's letters isn't it")
    }
}

enum LinkBlocklist {
    static func entries() throws -> [[String: Any]] {
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent("pipeline/website_blocklist.json")
        return try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: url)) as? [[String: Any]])
    }

    /// every .json file in the app bundle, subfolders included
    static func bundledJSON() -> [URL] {
        let root = Bundle.main.bundleURL
        let all = FileManager.default.enumerator(at: root, includingPropertiesForKeys: nil)?.allObjects as? [URL] ?? []
        return all.filter { $0.pathExtension == "json" && !$0.path.contains("/PlugIns/") }
    }

    private static func host(_ u: URLComponents) -> String {
        var h = (u.host ?? "").lowercased()
        if h.hasSuffix(".") { h.removeLast() }
        return h.hasPrefix("www.") ? String(h.dropFirst(4)) : h
    }

    private static func trimmedPath(_ p: String) -> String { p.hasSuffix("/") ? String(p.dropLast()) : p }

    /// the links in a JSON text that an entry covers: a "domain" entry its domain and subdomains, a "url" entry that page only
    static func hits(in text: String, _ entries: [[String: Any]]) -> [String] {
        let t = text.replacingOccurrences(of: "\\/", with: "/")
        let rx = try! NSRegularExpression(pattern: #"https?://[^"\s\\]+"#, options: [.caseInsensitive])
        return rx.matches(in: t, range: NSRange(t.startIndex..., in: t)).compactMap { m -> String? in
            let s = String(t[Range(m.range, in: t)!])
            guard let u = URLComponents(string: s) else { return nil }
            let h = host(u)
            for e in entries {
                if (e["match"] as? String ?? "domain") == "url" {
                    guard let v = URLComponents(string: e["url"] as? String ?? "") else { continue }
                    if !h.isEmpty && h == host(v) && trimmedPath(u.path) == trimmedPath(v.path) { return s }
                } else {
                    var d = (e["domain"] as? String ?? "").lowercased()
                    if let r = d.range(of: "://") { d = String(d[r.upperBound...]) }
                    d = String(d.split(separator: "/").first ?? "")
                    if d.hasPrefix("www.") { d = String(d.dropFirst(4)) }
                    if !d.isEmpty && (h == d || h.hasSuffix("." + d)) { return s }
                }
            }
            return nil
        }
    }
}

/// QA 2026-10-19, P1 3a: the support address is nick@eatsranked.com (Nick, 2026-10-12). The old Gmail address must not come back
/// anywhere in the app's source or bundled files.
final class SupportEmailTests: XCTestCase {
    func testSupportEmailIsEatsRanked() {
        XCTAssertEqual(Links.supportEmail, "nick@eatsranked.com")
    }

    func testNoGmailInAppSource() throws {
        let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent("RhodeIslandEats")
        XCTAssertGreaterThan(SupportEmailScan.textFiles(under: root).count, 5, "the app's source folder wasn't found")
        XCTAssertEqual(SupportEmailScan.hits(under: root), [], "the app's source still has a Gmail address")
    }

    /// The guard fires on a broken copy: a folder with one planted Gmail address.
    func testGmailGuardCatchesABrokenCopy() throws {
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: dir.appendingPathComponent("App"), withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: dir) }
        try "static let supportEmail = \"someone@GMAIL.com\"\n".write(to: dir.appendingPathComponent("App/Links.swift"), atomically: true, encoding: .utf8)
        try "{\"ok\": \"nick@eatsranked.com\"}".write(to: dir.appendingPathComponent("App/data.json"), atomically: true, encoding: .utf8)
        XCTAssertEqual(SupportEmailScan.hits(under: dir), ["App/Links.swift"])
    }
}

enum SupportEmailScan {
    static let textExtensions: Set<String> = ["swift", "plist", "json", "strings", "xcstrings", "xcprivacy", "md", "txt", "html", "entitlements"]

    static func textFiles(under root: URL) -> [URL] {
        let all = FileManager.default.enumerator(at: root, includingPropertiesForKeys: nil)?.allObjects as? [URL] ?? []
        return all.filter { textExtensions.contains($0.pathExtension.lowercased()) }
    }

    /// paths (relative to root) of text files that mention gmail.com, in any case
    static func hits(under root: URL) -> [String] {
        let base = root.resolvingSymlinksInPath().path + "/"
        return textFiles(under: root).compactMap { url in
            guard let text = try? String(contentsOf: url, encoding: .utf8),
                  text.range(of: "gmail.com", options: .caseInsensitive) != nil else { return nil }
            return url.resolvingSymlinksInPath().path.replacingOccurrences(of: base, with: "")
        }.sorted()
    }
}

/// QA 2026-10-19, P1 #13: outbound links ship without tracking tags (ref=google, referrer=google_food_ordering, cn_channel, utm_* …).
/// pipeline/tracking_params.py strips them in the export; these are the same rules.
final class TrackingParamTests: XCTestCase {
    func testNoTrackingParametersInBundledLinks() throws {
        let files = TrackingParams.bundledJSON()
        XCTAssertFalse(files.isEmpty, "no bundled JSON found")
        var hits: [String] = []
        for url in files {
            let text = try String(contentsOf: url, encoding: .utf8)
            hits += TrackingParams.tracked(in: text).map { "\(url.lastPathComponent): \($0)" }
        }
        XCTAssertEqual(hits, [], "links with tracking parameters in the app's bundled data")
    }

    /// The guard fires on a broken copy (four kinds of tracking tag, one in escaped JSON; then Georgia's four from QA 2026-10-28: after
    /// "#", in the path, without a scheme and Klaviyo's _kx) and leaves a store's own parameters, anchors and routes alone.
    func testTrackingGuardCatchesABrokenCopy() {
        let broken = #"[{"w":"https:\/\/places.example.com\/menu?ref=google"},{"w":"https://a.example/?utm_source=gmb&store=4"},"#
            + #"{"w":"https://b.example/x?referrer=google_food_ordering"},{"w":"https://c.example/order/1?cn_channel=cn_google"}]"#
        XCTAssertEqual(TrackingParams.tracked(in: broken).count, 4)
        // QA 2026-10-28 (P1 #4): Hard Rock Atlanta's Yext tag after "#", Snooze Alpharetta's tags written into the path, a Macon
        // Instagram link stored without a scheme, and Paul Thomas Chocolates' Klaviyo _kx
        let hidden = #"[{"w":"https:\/\/cafe.hardrock.com\/atlanta\/#utm_source=rest_of_network&utm_medium=Yext"},"#
            + #"{"w":"https://www.snoozeeatery.com/restaurant/georgia/alpharetta/utm_source=Facebook&utm_medium=BusinessListing"},"#
            + #"{"w":"instagram.com\/sharks1413_macon?igshid=NjNlMDhmYTc%3D"},"#
            + #"{"w":"https://paulthomaschocolates.com/pages/free-tasting-event?_kx=aSsBlo5n7gs8XtzVMZqf49qCxiL8_rle28VLXim4X1o.V26kig"}]"#
        XCTAssertEqual(TrackingParams.tracked(in: hidden).count, 4)
        let clean = #"[{"w":"https://order.example.com/menu?restaurantId=51&location=7"},{"w":"https://shop.example.com/?cid=12&ref=gs"},"#
            + #"{"w":"https://a.example.com/#menu"},{"w":"https://b.example.com/#/order?table=4"},{"w":"instagram.com/sharks1413_macon"}]"#
        XCTAssertEqual(TrackingParams.tracked(in: clean), [])
    }
}

enum TrackingParams {
    /// tracking by name, whatever the value
    static let keys = try! NSRegularExpression(pattern: #"^(?:utm[_-].*|gclid|gbraid|wbraid|dclid|fbclid|msclkid|mc_cid|mc_eid|_ga|_gl|_kx|igsh|"#
        + #"igshid|mibextid|srsltid|cn_channel|y_source|rwg_token|olonwp|ost_redirect_attribution|cmpid|yext_?.*)$"#, options: [.caseInsensitive])
    /// tracking only with these values
    static let values: [String: String] = ["ref": #"^(?:google|gmb|gbp|yext|bookmarks)\b"#, "referrer": "^google",
                                           "source": #"^(?:google|gmb|gbp|yext)\b"#, "cid": "^RF:YXT", "cmp": "^OKC-"]

    /// every .json file in the app bundle, subfolders included
    static func bundledJSON() -> [URL] {
        let all = FileManager.default.enumerator(at: Bundle.main.bundleURL, includingPropertiesForKeys: nil)?.allObjects as? [URL] ?? []
        return all.filter { $0.pathExtension == "json" && !$0.path.contains("/PlugIns/") }
    }

    static func isTracking(_ key: String, _ value: String) -> Bool {
        let k = key.trimmingCharacters(in: .whitespaces)
        if keys.firstMatch(in: k, range: NSRange(k.startIndex..., in: k)) != nil { return true }
        guard let pattern = values[k.lowercased()] else { return false }
        return value.trimmingCharacters(in: .whitespaces).range(of: pattern, options: [.regularExpression, .caseInsensitive]) != nil
    }

    /// links in a JSON text that still carry a tracking tag: in the query, after "#" (a route's own query, or "#utm_source=…"), or
    /// written into the path ("…/alpharetta/utm_source=Facebook&utm_medium=BusinessListing"), with or without a scheme
    /// ("instagram.com/x?igshid=…"); pipeline/tracking_params.py's rules since QA 2026-10-28 (P1 #4)
    static func tracked(in text: String) -> [String] {
        let t = text.replacingOccurrences(of: "\\/", with: "/").replacingOccurrences(of: "&amp;", with: "&")
        let rx = try! NSRegularExpression(pattern: #"https?://[^\s"'<>\\]+|(?<![\w/.:@-])(?:[a-z0-9-]+\.)+[a-z]{2,}/[^\s"'<>\\]*"#,
                                          options: [.caseInsensitive])
        return rx.matches(in: t, range: NSRange(t.startIndex..., in: t)).compactMap { m -> String? in
            let s = String(t[Range(m.range, in: t)!])
            return isTracked(s) ? s : nil
        }
    }

    static func isTracked(_ link: String) -> Bool {
        var rest = Substring(link)
        var fragment: Substring = ""
        if let h = rest.firstIndex(of: "#") { fragment = rest[rest.index(after: h)...]; rest = rest[..<h] }
        var query: Substring = ""
        if let q = rest.firstIndex(of: "?") { query = rest[rest.index(after: q)...]; rest = rest[..<q] }
        if hasTracking(query) { return true }
        if fragment.contains("=") {
            let tail = fragment.lastIndex(of: "?").map { fragment[fragment.index(after: $0)...] } ?? fragment
            if hasTracking(tail) { return true }
        }
        let afterScheme = rest.range(of: "://").map { rest[$0.upperBound...] } ?? rest
        let path = afterScheme.firstIndex(of: "/").map { afterScheme[$0...] } ?? ""
        return path.split(separator: "/").contains { $0.contains("=") && hasTracking($0) }
    }

    /// "k=v&k2=v2" holds a tracking pair
    static func hasTracking(_ params: Substring) -> Bool {
        for part in params.split(separator: "&") {
            let kv = part.split(separator: "=", maxSplits: 1, omittingEmptySubsequences: false)
            let k = String(kv[0]).replacingOccurrences(of: "+", with: " ").removingPercentEncoding ?? String(kv[0])
            let v = kv.count > 1 ? (String(kv[1]).replacingOccurrences(of: "+", with: " ").removingPercentEncoding ?? String(kv[1])) : ""
            if isTracking(k, v) { return true }
        }
        return false
    }
}

/// No Google-derived data ships: the app's calibration once carried Google 2021's open share per listing group (QA 2026-10-28, GA-1;
/// the same guard as sc-eats). Only the private web leaderboard may use the 2021 snapshot.
final class NoGoogleDataTests: XCTestCase {
    /// a key that names Google or something only Google's snapshot supplies
    static let googleKey = try! NSRegularExpression(pattern: "google|rating|review|gmap|price|in21|closed21", options: [.caseInsensitive])

    /// every Google-derived key in a decoded JSON value, as "path.key"
    static func googleKeys(in value: Any, path: String = "") -> [String] {
        if let d = value as? [String: Any] {
            return d.flatMap { k, v -> [String] in
                let here = path.isEmpty ? k : path + "." + k
                let hit = googleKey.firstMatch(in: k, range: NSRange(k.startIndex..., in: k)) != nil ? [here] : []
                return hit + googleKeys(in: v, path: here)
            }
        }
        if let a = value as? [Any] { return a.flatMap { googleKeys(in: $0, path: path + "[]") } }
        return []
    }

    func testNoGoogleDerivedKeyInBundledData() throws {
        let files = Bundle.main.urls(forResourcesWithExtension: "json", subdirectory: nil) ?? []
        XCTAssertFalse(files.isEmpty, "no bundled JSON found")
        var hits = Set<String>()
        for url in files {
            let value = try JSONSerialization.jsonObject(with: Data(contentsOf: url))
            for k in Self.googleKeys(in: value) { hits.insert(url.lastPathComponent + ": " + k) }
        }
        XCTAssertEqual(hits.sorted(), [], "Google-derived data in the app bundle")
    }

    /// The guard fires on a copy broken the way the first export was (an area's open_google_2021 shares) and on a place rating.
    func testGuardCatchesABrokenCopy() {
        let area = "Rhode Island (RIDOH food service licenses with seats, active in 2018)"
        let broken: [String: Any] = ["calibration": [area: ["groups": ["meta_high": ["n": 18644, "official": 0.192]],
                                                            "open_google_2021": ["meta_high": 0.706]]],
                                     "places": [["id": "x", "n": "Somewhere", "rating": 4.5]]]
        XCTAssertEqual(Set(Self.googleKeys(in: broken).map { $0.components(separatedBy: ".").last! }), ["open_google_2021", "rating"])
        XCTAssertEqual(Self.googleKeys(in: ["calibration": [area: ["groups": ["meta_high": ["n": 1, "official": 0.8]]]]]), [],
                       "the calibration the app needs passes")
    }
}
