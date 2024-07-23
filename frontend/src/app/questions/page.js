// src/app/questions/page.js
import { useRouter } from 'next/router';
import QuestionList from '../components/QuestionList';

export default function QuestionsPage() {
  const router = useRouter();
  const { state } = router.location;

  if (!state || !state.questions) {
    return <div>No questions generated. Please go back and generate questions.</div>;
  }

  return (
    <div>
      <QuestionList questions={state.questions} />
    </div>
  );
}
