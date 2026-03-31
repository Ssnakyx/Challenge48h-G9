<?php

namespace App\Form;

use App\Model\MapFilterData;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\DateType;
use Symfony\Component\Form\Extension\Core\Type\NumberType;
use Symfony\Component\Form\Extension\Core\Type\SubmitType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

class MapFilterType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('date', DateType::class, [
                'label' => 'Date',
                'widget' => 'single_text',
                'required' => false,
            ])
            ->add('indexMin', NumberType::class, [
                'label' => 'Score minimum',
                'required' => false,
                'attr' => ['placeholder' => '0', 'min' => 0, 'max' => 100],
            ])
            ->add('indexMax', NumberType::class, [
                'label' => 'Score maximum',
                'required' => false,
                'attr' => ['placeholder' => '100', 'min' => 0, 'max' => 100],
            ])
            ->add('searchArea', TextType::class, [
                'label' => 'Rechercher une station',
                'required' => false,
                'attr' => ['placeholder' => 'Nom de station…'],
            ])
            ->add('submit', SubmitType::class, [
                'label' => 'Filtrer',
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => MapFilterData::class,
            'method' => 'GET',
            'csrf_protection' => false,
        ]);
    }
}
