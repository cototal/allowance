<?php

namespace App\Controller;

use App\Entity\Entry;
use App\Form\EntryType;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

/**
 * @Route("/entry")
 */
class EntryController extends AbstractController
{
    /**
     * @var EntityManagerInterface
     */
    private $em;

    public function __construct(EntityManagerInterface $em)
    {
        $this->em = $em;
    }

    /**
     * @Route("/", name="entry_index", methods={"GET"})
     */
    public function index(): Response
    {
        $entries = $this->em->getRepository(Entry::class)->findBy([]);
        return $this->render('entry/index.html.twig', [
            'entries' => $entries
        ]);
    }

    /**
     * @Route("/new", name="entry_new", methods={"GET","POST"})
     */
    public function new(Request $request): Response
    {
        $entry = new Entry();
        $form = $this->createForm(EntryType::class, $entry);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->em->persist($entry);
            $this->em->flush();

            return $this->redirectToRoute("entry_show", ["id" => $entry->getId()]);
        }

        return $this->render('entry/new.html.twig', [
            'entry' => $entry,
            'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}", name="entry_show", methods={"GET"})
     */
    public function show(Entry $entry): Response
    {
        return $this->render('entry/show.html.twig', [
            "entry" => $entry,
        ]);
    }

    /**
     * @Route("/{id}/edit", name="entry_edit", methods={"GET","POST"})
     */
    public function edit(Request $request, Entry $entry): Response
    {
        $form = $this->createForm(EntryType::class, $entry);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->em->flush();

            return $this->redirectToRoute('entry_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('entry/edit.html.twig', [
            'entry' => $entry,
            'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}", name="entry_delete", methods={"DELETE"})
     * @param Request $request
     * @param Entry $entry
     * @return Response
     */
    public function delete(Request $request, Entry $entry): Response
    {
        if ($this->isCsrfTokenValid("delete" . $entry->getId(), $request->query->get("_token"))) {
            $this->em->remove($entry);
            $this->em->flush();
        }

        return $this->json(null, 204);
    }
}
