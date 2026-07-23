/*
 * The Living Past — blank locked template builder (SCOPE §7 group structure).
 * Creates the empty, pre-named layer-group skeleton at the locked master size
 * with guides, ready to receive art top-group to bottom-group without backtracking.
 *
 * Run from the repo root:
 *   osascript -e 'tell application "Adobe Photoshop 2024" to do javascript (read (POSIX file "/Users/ericeldridge/dino_art/tools/build_template_psd.jsx"))'
 * or open in Photoshop → File → Scripts → Browse.
 *
 * Values mirror living_past/template/design_tokens.json (canvas + layout).
 */
#target photoshop

(function () {
  // ---- locked canvas (design_tokens.canvas) ----
  var FULL_W = 10875, FULL_H = 7275;      // full bleed px
  var TRIM_W = 10800, TRIM_H = 7200;      // trim px
  var DPI = 300;
  var BLEED = 37.5, SAFE = 75;            // px
  var rowsPct = { scene: 65, guide: 21, facts: 10, timeline: 4 };

  var doc = app.documents.add(
    new UnitValue(FULL_W, "px"), new UnitValue(FULL_H, "px"),
    DPI, "The_Living_Past_V5_template",
    NewDocumentMode.RGB, DocumentFill.TRANSPARENT
  );
  app.preferences.rulerUnits = Units.PIXELS;

  // ---- guides (trim, safe, row boundaries, coastline) ----
  function vGuide(x) { doc.guides.add(Direction.VERTICAL, new UnitValue(x, "px")); }
  function hGuide(y) { doc.guides.add(Direction.HORIZONTAL, new UnitValue(y, "px")); }
  // trim box
  vGuide(BLEED); vGuide(FULL_W - BLEED); hGuide(BLEED); hGuide(FULL_H - BLEED);
  // safe margin
  vGuide(BLEED + SAFE); vGuide(FULL_W - BLEED - SAFE);
  hGuide(BLEED + SAFE); hGuide(FULL_H - BLEED - SAFE);
  // row boundaries within trim height, offset by top bleed
  var y = BLEED, order = ["scene", "guide", "facts", "timeline"];
  for (var i = 0; i < order.length; i++) {
    y += TRIM_H * (rowsPct[order[i]] / 100);
    if (i < order.length - 1) hGuide(y);
  }
  // coastline at 48% of trim width
  vGuide(BLEED + TRIM_W * 0.48);

  // ---- §7 top-level group structure (back to front) ----
  function group(name, parent) {
    var g = (parent || doc).layerSets.add();
    g.name = name;
    return g;
  }
  function placeholder(name, parent) {
    // empty pixel layer as a named home
    var L = parent.artLayers.add();
    L.name = name;
    return L;
  }

  group("00_GUIDES");
  group("10_SKY");
  var sky = doc.layerSets.getByName("10_SKY");
  placeholder("asteroid_whisper", sky);

  group("20_BACKGROUND");
  group("30_LAND_MIDGROUND");

  var org = group("40_ORGANISMS");
  var zones = ["ABOVE", "UNDER", "SHORE", "OCEAN"];
  for (var z = 0; z < zones.length; z++) group(zones[z], org);

  group("50_UNDERGROUND");
  group("60_OCEAN_COLUMN");
  group("70_WORLD_GRADE");

  var furn = group("80_FURNITURE");
  var furnGroups = ["title", "timeline", "globe", "cards_32", "qr_codes",
                    "callout_numbers", "legends", "confidence_badges",
                    "scale_key", "credits"];
  for (var f = 0; f < furnGroups.length; f++) group(furnGroups[f], furn);

  // Photoshop adds new groups at top; reverse so 00_GUIDES ends on top of the stack
  // (back-to-front build order reads top→bottom in the Layers panel).
  // (Left as created; artist can reorder if desired — names are the contract.)

  alert("Living Past template built:\n" + FULL_W + "x" + FULL_H + " @ " + DPI + "dpi\n" +
        "Groups: 00_GUIDES → 80_FURNITURE (see SCOPE §7).\nSave As .psd into living_past/template/.");
})();
