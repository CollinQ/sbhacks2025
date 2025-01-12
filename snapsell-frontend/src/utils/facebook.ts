export async function postItemsToFacebookMarketplace(items: any[]) {
  try {
    // Filter for only unlisted items
    const unlistedItems = items.filter(item => item.status === 'unlisted');
    console.log(unlistedItems)
    // Track overall progress
    let totalItems = unlistedItems.length;
    let completedItems = 0;

    // Process items sequentially
    for (const item of unlistedItems) {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/post_to_facebook`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ item })
        });

        if (!response.ok) {
          console.error(`Failed to post item ${item.title} to Facebook Marketplace`);
          continue;
        }

        completedItems++;
        console.log(`Posted item ${completedItems}/${totalItems} to Facebook: ${item.title}`);

      } catch (itemError) {
        console.error(`Error posting item ${item.title}:`, itemError);
        // Continue with next item even if one fails
      }
    }

    return {
      success: true,
      message: `Posted ${completedItems}/${totalItems} items to Facebook Marketplace`
    };

  } catch (error) {
    console.error('Error posting to Facebook Marketplace:', error);
    throw error;
  }
}