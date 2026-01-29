function BadgeCard({ img_path, title }) {
  return (
    <div
      className='flex flex-col h-max w-max
        text-white italic font-semibold gap-5 items-center rounded'
    >
      <img src={img_path} alt='' className='h-32 w-32 rounded-full shrink-0 border-green-700 border-4 ring-4 ring-offset-2 ring-green-700' />
      <h3 className="rounded-sm p-2 border-2">{title}</h3>
    </div>
  );
}

export default BadgeCard;
