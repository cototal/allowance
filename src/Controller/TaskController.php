<?php

namespace App\Controller;

use App\Entity\Task;
use App\Form\TaskType;
use App\Form\TaskUpdateType;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route("/task")]
class TaskController extends AbstractController
{
    private ?EntityManagerInterface $em;

    public function __construct(EntityManagerInterface $em)
    {
        $this->em = $em;
    }

    #[Route("/new", name: "task_new", methods: ["GET", "POST"])]
    public function new(Request $request): Response
    {
        if (!$this->getUser()->getTasks()->isEmpty()) {
            $this->addFlash("alert", "You may only set one task");
            return $this->redirectToRoute("entry_index");
        }
        $task = new Task();
        $form = $this->createForm(TaskType::class, $task);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $task->setUser($this->getUser());
            $this->em->persist($task);
            $this->em->flush();

            return $this->redirectToRoute("entry_index");
        }

        return $this->render('task/new.html.twig', [
            'task' => $task,
            'form' => $form->createView(),
        ]);
    }

    #[Route("/{id}/edit", name: "task_edit", methods: ["GET", "POST"])]
    public function edit(Request $request, Task $task): Response
    {
        $form = $this->createForm(TaskUpdateType::class, $task);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->em->flush();

            return $this->redirectToRoute('entry_index');
        }

        return $this->render('task/edit.html.twig', [
            'task' => $task,
            'form' => $form->createView(),
        ]);
    }

    #[Route("/{id}", name: "task_delete", methods: ["DELETE"])]
    public function delete(Request $request, Task $task): Response
    {
        if ($this->isCsrfTokenValid("delete" . $task->getId(), $request->query->get("_token"))) {
            $this->em->remove($task);
            $this->em->flush();
        }

        return $this->json(null, 204);
    }
}
