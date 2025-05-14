import { PostsFeed } from '@/components/PostsFeed';

const RssFeed = () => {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">RSS Feeds</h1>
      <PostsFeed platformFilter="RSS" />
    </div>
  );
};

export default RssFeed; 