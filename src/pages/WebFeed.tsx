import { PostsFeed } from '@/components/PostsFeed';

const WebFeed = () => (
  <div className="container mx-auto py-8">
    <h1 className="text-2xl font-bold mb-6">Web Feed</h1>
    <PostsFeed platformFilter="Website" />
  </div>
);

export default WebFeed; 