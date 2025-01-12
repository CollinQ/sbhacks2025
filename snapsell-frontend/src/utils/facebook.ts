import { Item } from '../types/item';

export async function postItemsToFacebookMarketplace(items: Item[]) {
  try {
    const unlistedItems = items.filter(item => item.status === 'unlisted');
    console.log(`Found ${unlistedItems.length} unlisted items to post`);

    // Process items sequentially
    for (const item of unlistedItems) {
      console.log('Posting item:', item.title);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/post_to_facebook`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item: {
            id: item.id,
            user_id: item.user_id,
            image_url: item.image_url,
            title: item.title,
            description: item.description,
            price: item.price,
            condition: item.condition,
            status: item.status,
            created_at: item.created_at,
            updated_at: item.updated_at
          }
        })
      });

      if (!response.ok) {
        console.error(`Failed to post item: ${item.title}`);
        throw new Error(`Failed to post item: ${item.title}`);
      }

      console.log(`Successfully posted item: ${item.title}`);
    }
    
    return {
      success: true,
      message: `Posted ${unlistedItems.length} items to Facebook Marketplace`
    };

  } catch (error) {
    console.error('Error posting to Facebook Marketplace:', error);
    throw error;
  }
}