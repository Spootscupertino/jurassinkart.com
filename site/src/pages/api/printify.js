export async function GET() {
  const apiKey = import.meta.env.PRINTIFY_API_KEY;
  const configuredShopId = import.meta.env.PRINTIFY_SHOP_ID;
  const authHeaders = {
    'Authorization': `Bearer ${apiKey}`
  };

  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Missing PRINTIFY_API_KEY in .env' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const shopIds = [];

  if (configuredShopId) {
    shopIds.push(String(configuredShopId));
  } else {
    const shopsResponse = await fetch('https://api.printify.com/v1/shops.json', {
      headers: authHeaders
    });

    if (!shopsResponse.ok) {
      const details = await shopsResponse.text();
      return new Response(JSON.stringify({
        error: 'Failed to fetch shops from Printify',
        status: shopsResponse.status,
        details
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const shops = await shopsResponse.json();
    for (const shop of shops || []) {
      if (shop?.id) shopIds.push(String(shop.id));
    }

    if (shopIds.length === 0) {
      return new Response(JSON.stringify({
        error: 'No shops found for this Printify account. Set PRINTIFY_SHOP_ID in .env if needed.'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  let allProducts = [];
  const shopErrors = [];

  for (const shopId of shopIds) {
    const response = await fetch(`https://api.printify.com/v1/shops/${shopId}/products.json?limit=50`, {
      headers: authHeaders
    });

    if (!response.ok) {
      const details = await response.text();
      shopErrors.push({ shopId, status: response.status, details });
      continue;
    }

    const data = await response.json();
    const products = Array.isArray(data?.data) ? data.data : [];
    allProducts = allProducts.concat(products.map((product) => ({ ...product, __shopId: shopId })));
  }

  if (allProducts.length === 0) {
    return new Response(JSON.stringify({
      error: 'Failed to fetch products from Printify',
      shopIds,
      details: shopErrors
    }, null, 2), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const phoneCasePattern = /phone\s*case|iphone|samsung\s*galaxy|pixel\s*case|airpods\s*case|mag\s*safe|impact-resistant\s*cases|tough\s*phone\s*cases/i;
  const posterCanvasPattern = /poster|canvas|wrapped\s*canvas|stretched\s*canvas|framed\s*poster|framed\s*print|matte\s*poster|rolled\s*poster|wall\s*art|wall\s*decor/i;
  const artSubjectPattern = /dinosaur|jurassic|prehistoric|paleo|fossil|art|illustration|painting/i;

  const scoredProducts = allProducts.map((product) => {
    const title = product.title || '';
    const description = product.description || '';
    const tags = Array.isArray(product.tags) ? product.tags.join(' ') : '';
    const searchable = `${title} ${description} ${tags}`;

    const isPhoneCase = phoneCasePattern.test(searchable);
    const isPosterOrCanvas = posterCanvasPattern.test(searchable);
    const isArtSubject = artSubjectPattern.test(searchable);
    const hasImage = Boolean(product.images?.[0]?.src);

    let score = 0;
    if (isPosterOrCanvas) score += 80;
    if (isArtSubject) score += 25;
    if (hasImage) score += 10;
    if (isPhoneCase) score -= 200;

    return {
      id: product.id,
      shopId: product.__shopId,
      title,
      description,
      image: product.images?.[0]?.src || null,
      isPhoneCase,
      isPosterOrCanvas,
      isArtSubject,
      hasImage,
      score
    };
  });

  const nonPhoneProducts = scoredProducts.filter((item) => !item.isPhoneCase && item.hasImage);
  const posterCanvasOnly = nonPhoneProducts.filter((item) => item.isPosterOrCanvas);
  const prioritizedPool = posterCanvasOnly.length > 0
    ? posterCanvasOnly
    : nonPhoneProducts.filter((item) => item.isArtSubject);

  // Deduplicate products based on normalized titles to prevent showing the same artwork across different mediums (e.g., both Canvas and Poster)
  const seenTitles = new Set();
  const deduplicatedPool = [];
  
  for (const item of prioritizedPool) {
    // Strip common product suffixes and normalize to a root art title
    const normTitle = (item.title || '').toLowerCase()
      .replace(/poster|canvas|wrapped|stretched|framed|matte|premium|rolled|print|wall\s*art|wall\s*decor/g, '')
      .replace(/[^a-z0-9]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
      
    if (!seenTitles.has(normTitle) && normTitle.length > 0) {
      seenTitles.add(normTitle);
      deduplicatedPool.push(item);
    } else if (normTitle.length === 0) {
      // Fallback if the title was literally just "poster" or something edge-case
      deduplicatedPool.push(item);
    }
  }

  const prioritized = deduplicatedPool
    .sort((a, b) => b.score - a.score)
    .slice(0, 16)
    .map(({ isPhoneCase, isPosterOrCanvas, isArtSubject, hasImage, score, ...publicFields }) => publicFields);

  return new Response(JSON.stringify(prioritized, null, 2), {
    headers: { 'Content-Type': 'application/json' }
  });
}
