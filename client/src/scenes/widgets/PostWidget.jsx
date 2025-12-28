import { MessageCircle, Heart, Share2, MoreHorizontal } from "lucide-react";
import FlexBetween from "components/FlexBetween";
import Friend from "components/Friends";
import WidgetWrapper from "components/WidgetWrapper";
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setPost } from "state";
import { API_ENDPOINTS } from "config/api";
import { motion, AnimatePresence } from "framer-motion";

const PostWidget = ({
  postId,
  postUserId,
  name,
  description,
  location,
  picturePath,
  userPicturePath,
  likes,
  comments,
}) => {
  const [isComments, setIsComments] = useState(false);
  const dispatch = useDispatch();
  const token = useSelector((state) => state.token);
  const user = useSelector((state) => state.user);
  const loggedInUserId = user?._id;
  const isLiked = Boolean(likes[loggedInUserId]);
  const likesCount = Object.keys(likes).length;

  const patchLike = async () => {
    const response = await fetch(`${API_ENDPOINTS.POSTS}/${postId}/like`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ userId: loggedInUserId }),
    });
    const updatedPost = await response.json();
    dispatch(setPost({ post: updatedPost }));
  };

  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    return `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/assets/${path}`;
  };

  return (
    <WidgetWrapper className="linkedin-card p-4">
      <div className="flex justify-between items-start mb-3">
        <Friend
          friendId={postUserId}
          name={name}
          subtitle={location}
          userPicturePath={userPicturePath}
        />
        <button className="p-1.5 hover:bg-grey-100 dark:hover:bg-grey-700 rounded-full transition-colors">
          <MoreHorizontal className="w-5 h-5 text-grey-500" />
        </button>
      </div>

      <p className="text-sm text-grey-800 dark:text-grey-100 leading-relaxed whitespace-pre-line px-1">
        {description}
      </p>

      {picturePath && (
        <div className="mt-3 -mx-4">
          <img
            className="w-full h-auto max-h-[500px] object-cover"
            alt="post"
            src={getImageUrl(picturePath)}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        </div>
      )}

      <div className="flex items-center justify-between mt-3 px-1">
        <div className="flex items-center gap-1">
          <div className="flex -space-x-1">
            <div className="bg-primary-500 rounded-full p-0.5 border border-white dark:border-grey-800">
              <Heart className="w-2.5 h-2.5 fill-white text-white" />
            </div>
          </div>
          <span className="text-[10px] text-grey-500 dark:text-grey-400 hover:text-primary-500 hover:underline cursor-pointer">
            {likesCount}
          </span>
        </div>
        <span className="text-[10px] text-grey-500 dark:text-grey-400 hover:text-primary-500 hover:underline cursor-pointer">
          {comments.length} comments
        </span>
      </div>

      <div className="border-t border-grey-100 dark:border-grey-700 mt-2 pt-1" />

      <div className="flex items-center justify-between">
        <button
          onClick={patchLike}
          className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-grey-50 dark:hover:bg-grey-700 rounded-md transition-colors group"
        >
          <Heart className={`w-5 h-5 ${isLiked ? 'fill-primary-500 text-primary-500' : 'text-grey-500 group-hover:text-primary-500'}`} />
          <span className={`text-sm font-semibold ${isLiked ? 'text-primary-500' : 'text-grey-500'}`}>Like</span>
        </button>

        <button
          onClick={() => setIsComments(!isComments)}
          className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-grey-50 dark:hover:bg-grey-700 rounded-md transition-colors group"
        >
          <MessageCircle className="w-5 h-5 text-grey-500 group-hover:text-primary-500" />
          <span className="text-sm font-semibold text-grey-500">Comment</span>
        </button>

        <button className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-grey-50 dark:hover:bg-grey-700 rounded-md transition-colors group">
          <Share2 className="w-5 h-5 text-grey-500 group-hover:text-primary-500" />
          <span className="text-sm font-semibold text-grey-500">Share</span>
        </button>
      </div>

      <AnimatePresence>
        {isComments && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-4 space-y-3"
          >
            {comments.map((comment, i) => (
              <div key={`${name}-${i}`} className="flex gap-2">
                <div className="flex-1 bg-grey-50 dark:bg-grey-700 p-3 rounded-lg">
                  <p className="text-xs font-bold text-grey-800 dark:text-grey-100">User Name</p>
                  <p className="text-xs text-grey-600 dark:text-grey-300 mt-1">{comment}</p>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </WidgetWrapper>
  );
};

export default PostWidget;