import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("RHODE ISLAND EATS").displayFont(32).foregroundStyle(Theme.green)
                    Text("A free guide to \(model.restaurantCount.formatted()) Rhode Island restaurants in all 39 cities and towns, with James Beard honors and hand-checked lists of Rhode Island's own food: hot wieners, clam shacks, Federal Hill, pizza strips and more. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("Rhode Island Eats is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the State of Rhode Island, the Rhode Island Department of Health, the Department of Business Regulation, RIGIS, the University of Rhode Island, any city or town, Visit Rhode Island, the James Beard Foundation, Apple, or any restaurant or chain. Other names are trademarks of their owners.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Hand-checked lists (hot wieners, clam shacks and stuffies, Federal Hill Italian, bakery pizza strips, Portuguese kitchens, frozen lemonade and creameries, oldest places) include only places checked against a 2025 or 2026 source (local news, a dated magazine guide or the place's own website), with the address checked. Founding years mean the year it opened at this address.")
                Text("Honors are James Beard Foundation winners, finalists and America's Classics, each checked against the Foundation's announcements or dated news. Rhode Island has no MICHELIN Guide.")
                Text("Rhode Island publishes no open list of its restaurants: the Department of Health's food service lists sit behind a bot check that this app never works around. So the app starts from open map listings (Overture Maps) and keeps the kinds that proved reliable: checked against the Department of Health's own 2018 license export, high-confidence listings matched far more often than the kinds left out. Each place's town is the city or town its pin falls in; village names (Wakefield, Galilee, Block Island) stay searchable. RIGIS's 2025 list of licensed food markets marks grocery and convenience counters as non-restaurants. Adult clubs are left out. Website links are checked, and any that no longer belong to the place are left out.")
                Text("The Department of Health's Center for Food Protection is the one restaurant inspector for the whole state. Its reports list the violations found, with no score, grade or placard, and they are published only in the department's own search, not as data, so this app shows no inspection results and computes no grade; each place links to the search.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("Rhode Island Department of Health", "Food establishment inspection reports, in the department's own search. Linked from each place; not copied. Its 2018 license export (RIDOH's L2K Food Facilities layer) was used only to measure how often each kind of map listing matched a licensed restaurant; no license or result from it is shown.", Links.inspections.absoluteString)
                source("RIGIS", "Licensed Food Markets (\(model.permitsUpdated)), RI Division of Statewide Planning from the Department of Health's licenses, provided \u{201C}as is\u{201D}; town outlines from Municipalities (1997). Rhode Island Geographic Information System (RIGIS) data, acknowledged as RIGIS asks. Used to mark grocery counters and to give each place its town; modified for this app.", Links.markets.absoluteString)
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org)\(model.overtureRelease.map { ", release \($0)" } ?? ""), filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. \(foursquareCopyright) Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.\nResearched places are put on the map with Overture Maps addresses data (open address sources under permissive licenses, docs.overturemaps.org/attribution).", "https://overturemaps.org")
                source("Honors", "James Beard Foundation awards, finalists and America's Classics are reported as facts and checked by hand against the official announcements. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", "https://www.jamesbeard.org/awards")
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                DataUpdatesNote()
                    .font(.footnote).foregroundStyle(Theme.muted)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(DayFormat.text(model.generated) ?? model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.green)
    }

    /// the copyright line exactly as the bundled Foursquare NOTICE has it, so the two can't disagree
    private var foursquareCopyright: String {
        guard let url = Bundle.main.url(forResource: "Foursquare-NOTICE", withExtension: "txt"),
              let text = try? String(contentsOf: url, encoding: .utf8),
              let line = text.split(separator: "\n").first(where: { $0.hasPrefix("©") }) else { return "© Foursquare Labs, Inc. All rights reserved." }
        return line.trimmingCharacters(in: .whitespaces)
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .inlineTitle(title)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
