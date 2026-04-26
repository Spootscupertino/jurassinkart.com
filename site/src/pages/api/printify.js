export async function GET() {
  const apiKey = import.meta.env.PRINTIFY_API_KEY;
  const configuredShopId = import.meta.env.PRINTIFY_SHOP_ID;

  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Missing PRINTIFY_API_KEY in .env' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  let shopId = configuredShopId;

  if (!shopId) {
    const shopsResponse = await fetch('https://api.printify.com/v1/shops.json', {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
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
    shopId = shops?.[0]?.id ? String(shops[0].id) : null;

    if (!shopId) {
      return new Response(JSON.stringify({
        error: 'No shops found for this Printify account. Set PRINTIFY_SHOP_ID in .env if needed.'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  const response = await fetch(`https://api.printify.com/v1/shops/${shopId}/products.json?limit=50`, {
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  if (!response.ok) {
    const details = await response.text();
    return new Response(JSON.stringify({
      error: 'Failed to fetch products from Printify',
      shopId,
      status: response.status,
      details
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const data = await response.json();

  const phoneCasePattern = /phone\s*case|iphone|samsung\s*galaxy|pixel\s*case|airpods\s*case|mag\s*safe/i;
  const posterCanvasPattern = /poster|canvas|wrapped\s*canvas|framed\s*poster|wall\s*art|print/i;
  const testPattern = /\btest\b|sample|default|placeholder|do\s*not\s*buy/i;

  const scoredProducts = (data.data || []).map((product) => {
    const title = product.title || '';
    const description = product.description || '';
    const searchable = `${title} ${description}`;

    const isPhoneCase = phoneCasePattern.test(searchable);
    const isPosterOrCanvas = posterCanvasPattern.test(searchable);
    const isTestItem = testPattern.test(searchable);

    let score = 0;
    if (isPosterOrCanvas) score += 80;
    if (isPhoneCase) score -= 80;
    if (isTestItem) score -= 120;

    return {
      id: product.id,
      title,
      description,
      image: product.images?.[0]?.src || null,
      isPhoneCase,
      isPosterOrCanvas,
      isTestItem,
      score
    };
  });

  const withoutTestItems = scoredProducts.filter((item) => !item.isTestItem);
  const showcaseFirst = withoutTestItems.length > 0 ? withoutTestItems : scoredProducts;
  const withoutPhoneCases = showcaseFirst.filter((item) => !item.isPhoneCase);

  const prioritized = (withoutPhoneCases.length >= 6 ? withoutPhoneCases : showcaseFirst)
    .sort((a, b) => b.score - a.score)
    .slice(0, 16)
    .map(({ isPhoneCase, isPosterOrCanvas, isTestItem, score, ...publicFields }) => publicFields);

  return new Response(JSON.stringify(prioritized, null, 2), {
    headers: { 'Content-Type': 'application/json' }
  });
}
